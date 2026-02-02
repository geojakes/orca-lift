"""Equipment configuration commands."""

import click

from ..db.repositories import EquipmentConfigRepository, UserProfileRepository
from ..models.equipment import EquipmentConfig, STANDARD_PLATE_SETS
from ..models.exercises import EquipmentType
from .base import async_command, echo_error, echo_info, echo_success, ensure_initialized


@click.group()
def equipment():
    """Manage equipment configuration.

    Configure available equipment, plate inventory, and weight settings.
    This affects which exercises the AI agents will recommend.
    """
    pass


@equipment.command("configure")
@click.pass_context
@async_command
async def configure(ctx: click.Context):
    """Interactively configure equipment settings.

    Walks through equipment types, plate inventory, and other settings
    to customize program generation for your home gym or commercial gym.
    """
    ensure_initialized(ctx)

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get_latest()

    if not profile:
        echo_error("No user profile found. Run 'orca-lift init' first.")
        ctx.exit(1)

    click.echo("\n" + click.style("Equipment Configuration", bold=True))
    click.echo("=" * 40)
    click.echo()

    # Weight unit
    weight_unit = click.prompt(
        "Weight unit",
        type=click.Choice(["lb", "kg"]),
        default="lb",
    )

    # Barbell weight
    default_barbell = 45.0 if weight_unit == "lb" else 20.0
    barbell_weight = click.prompt(
        f"Barbell weight ({weight_unit})",
        type=float,
        default=default_barbell,
    )

    # Dumbbell max
    has_dumbbells = click.confirm("Do you have dumbbells?", default=True)
    dumbbell_max = None
    if has_dumbbells:
        default_db_max = 100.0 if weight_unit == "lb" else 45.0
        dumbbell_max = click.prompt(
            f"Maximum dumbbell weight ({weight_unit})",
            type=float,
            default=default_db_max,
        )

    # Plate inventory
    plate_inventory = None
    configure_plates = click.confirm(
        "Configure plate inventory for accurate weight rounding?",
        default=True,
    )

    if configure_plates:
        click.echo("\nPlate inventory options:")
        click.echo("  1. Home gym (basic)")
        click.echo("  2. Home gym (full)")
        click.echo("  3. Commercial gym")
        click.echo("  4. Custom")

        plate_choice = click.prompt(
            "Select option",
            type=click.IntRange(1, 4),
            default=1,
        )

        if plate_choice == 1:
            key = f"home_basic_{weight_unit}"
            plate_inventory = STANDARD_PLATE_SETS.get(key, {})
        elif plate_choice == 2:
            key = f"home_full_{weight_unit}"
            plate_inventory = STANDARD_PLATE_SETS.get(key, {})
        elif plate_choice == 3:
            key = f"commercial_gym_{weight_unit}"
            plate_inventory = STANDARD_PLATE_SETS.get(key, {})
        else:
            # Custom entry
            click.echo("\nEnter plate pairs (0 to skip):")
            plate_inventory = {}

            if weight_unit == "lb":
                plate_weights = [45, 35, 25, 10, 5, 2.5]
            else:
                plate_weights = [20, 15, 10, 5, 2.5, 1.25]

            for weight in plate_weights:
                pairs = click.prompt(
                    f"  {weight}{weight_unit} plates (pairs)",
                    type=int,
                    default=0,
                )
                if pairs > 0:
                    plate_inventory[weight] = pairs

    # Create config
    config = EquipmentConfig(
        profile_id=profile.id,
        plate_inventory=plate_inventory if plate_inventory else None,
        weight_unit=weight_unit,
        barbell_weight=barbell_weight,
        dumbbell_max=dumbbell_max,
    )

    # Save
    config_repo = EquipmentConfigRepository()
    await config_repo.upsert(config)

    click.echo()
    echo_success("Equipment configuration saved!")
    click.echo()
    click.echo(config.get_summary())


@equipment.command("show")
@click.pass_context
@async_command
async def show(ctx: click.Context):
    """Display current equipment configuration."""
    ensure_initialized(ctx)

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get_latest()

    if not profile:
        echo_error("No user profile found. Run 'orca-lift init' first.")
        ctx.exit(1)

    config_repo = EquipmentConfigRepository()
    config = await config_repo.get_by_profile(profile.id)

    if not config:
        echo_info("No equipment configuration found.")
        click.echo("Run 'orca-lift equipment configure' to set up your equipment.")
        return

    click.echo("\n" + click.style("Equipment Configuration", bold=True))
    click.echo("=" * 40)
    click.echo(config.get_summary())

    # Also show equipment types from profile
    click.echo()
    click.echo(click.style("Available Equipment Types:", bold=True))
    for eq in profile.available_equipment:
        click.echo(f"  - {eq.value}")


@equipment.command("set")
@click.option("--plates", help="Plate inventory (format: '45:4,25:4,10:2,5:2,2.5:2')")
@click.option("--unit", type=click.Choice(["lb", "kg"]), help="Weight unit")
@click.option("--barbell", type=float, help="Barbell weight")
@click.option("--dumbbell-max", type=float, help="Maximum dumbbell weight")
@click.pass_context
@async_command
async def set_config(
    ctx: click.Context,
    plates: str | None,
    unit: str | None,
    barbell: float | None,
    dumbbell_max: float | None,
):
    """Set equipment configuration directly.

    Examples:

        # Set plates for home gym
        orca-lift equipment set --plates "45:4,25:4,10:2,5:2,2.5:2" --unit lb

        # Set barbell weight
        orca-lift equipment set --barbell 45

        # Set max dumbbell weight
        orca-lift equipment set --dumbbell-max 100
    """
    ensure_initialized(ctx)

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get_latest()

    if not profile:
        echo_error("No user profile found. Run 'orca-lift init' first.")
        ctx.exit(1)

    config_repo = EquipmentConfigRepository()
    config = await config_repo.get_by_profile(profile.id)

    # Create new config if none exists
    if not config:
        config = EquipmentConfig(
            profile_id=profile.id,
            weight_unit=unit or "lb",
            barbell_weight=barbell or 45.0,
        )

    # Update with provided values
    if unit:
        config.weight_unit = unit
    if barbell is not None:
        config.barbell_weight = barbell
    if dumbbell_max is not None:
        config.dumbbell_max = dumbbell_max

    # Parse plates string
    if plates:
        plate_inventory = {}
        for item in plates.split(","):
            if ":" in item:
                weight_str, count_str = item.split(":")
                try:
                    weight = float(weight_str.strip())
                    count = int(count_str.strip())
                    plate_inventory[weight] = count
                except ValueError:
                    echo_error(f"Invalid plate format: {item}")
                    ctx.exit(1)
        config.plate_inventory = plate_inventory

    # Save
    await config_repo.upsert(config)

    echo_success("Equipment configuration updated!")
    click.echo()
    click.echo(config.get_summary())


@equipment.command("preset")
@click.argument("preset_name", type=click.Choice([
    "home_basic_lb", "home_full_lb", "commercial_gym_lb",
    "home_basic_kg", "home_full_kg"
]))
@click.pass_context
@async_command
async def preset(ctx: click.Context, preset_name: str):
    """Apply a preset plate inventory configuration.

    Available presets:

        home_basic_lb    - Basic home gym (lb)
        home_full_lb     - Full home gym (lb)
        commercial_gym_lb - Commercial gym (lb)
        home_basic_kg    - Basic home gym (kg)
        home_full_kg     - Full home gym (kg)
    """
    ensure_initialized(ctx)

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get_latest()

    if not profile:
        echo_error("No user profile found. Run 'orca-lift init' first.")
        ctx.exit(1)

    if preset_name not in STANDARD_PLATE_SETS:
        echo_error(f"Unknown preset: {preset_name}")
        ctx.exit(1)

    # Determine weight unit from preset name
    weight_unit = "kg" if preset_name.endswith("_kg") else "lb"
    barbell_weight = 20.0 if weight_unit == "kg" else 45.0

    config = EquipmentConfig(
        profile_id=profile.id,
        plate_inventory=STANDARD_PLATE_SETS[preset_name],
        weight_unit=weight_unit,
        barbell_weight=barbell_weight,
    )

    config_repo = EquipmentConfigRepository()
    await config_repo.upsert(config)

    echo_success(f"Applied preset: {preset_name}")
    click.echo()
    click.echo(config.get_summary())
