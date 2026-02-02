"""Equipment configuration routes."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ...db.repositories import EquipmentConfigRepository, UserProfileRepository
from ...models.equipment import EquipmentConfig, STANDARD_PLATE_SETS

router = APIRouter(prefix="/equipment", tags=["equipment"])


def get_templates(request: Request):
    """Get templates from app state."""
    return request.app.state.templates


@router.get("", response_class=HTMLResponse)
async def equipment_page(request: Request):
    """Equipment configuration page."""
    templates = get_templates(request)

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get_latest()

    config = None
    if profile:
        config_repo = EquipmentConfigRepository()
        config = await config_repo.get_by_profile(profile.id)

    return templates.TemplateResponse(
        "equipment.html",
        {
            "request": request,
            "profile": profile,
            "config": config,
            "presets": list(STANDARD_PLATE_SETS.keys()),
        },
    )


@router.post("")
async def save_equipment(
    request: Request,
    weight_unit: str = Form("lb"),
    barbell_weight: float = Form(45.0),
    dumbbell_max: float | None = Form(None),
    plate_preset: str | None = Form(None),
    custom_plates: str | None = Form(None),
):
    """Save equipment configuration."""
    profile_repo = UserProfileRepository()
    profile = await profile_repo.get_latest()

    if not profile:
        return RedirectResponse(url="/equipment?error=no_profile", status_code=302)

    # Parse plate inventory
    plate_inventory = None
    if plate_preset and plate_preset in STANDARD_PLATE_SETS:
        plate_inventory = STANDARD_PLATE_SETS[plate_preset]
    elif custom_plates:
        plate_inventory = {}
        for item in custom_plates.split(","):
            if ":" in item:
                weight_str, count_str = item.split(":")
                try:
                    weight = float(weight_str.strip())
                    count = int(count_str.strip())
                    plate_inventory[weight] = count
                except ValueError:
                    continue

    config = EquipmentConfig(
        profile_id=profile.id,
        plate_inventory=plate_inventory,
        weight_unit=weight_unit,
        barbell_weight=barbell_weight,
        dumbbell_max=dumbbell_max,
    )

    config_repo = EquipmentConfigRepository()
    await config_repo.upsert(config)

    return RedirectResponse(url="/equipment?saved=true", status_code=302)


@router.get("/api/config")
async def get_equipment_config(request: Request):
    """Get equipment configuration as JSON."""
    profile_repo = UserProfileRepository()
    profile = await profile_repo.get_latest()

    if not profile:
        return {"error": "No profile found"}

    config_repo = EquipmentConfigRepository()
    config = await config_repo.get_by_profile(profile.id)

    if not config:
        return {"error": "No equipment config found"}

    return config.to_dict()
