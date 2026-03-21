"""Full Liftoscript specification for the AI converter.

This contains the complete grammar, exercise list, examples, and all
advanced features of the Liftoscript DSL used by Liftosaur.
"""

LIFTOSCRIPT_FULL_SPEC = r"""
# Liftoscript

Liftoscript is a domain-specific language for writing weightlifting programs in Liftosaur app. It allows users to define their workout routines in a text format, specifying exercises, sets, reps, weights, RPE, timers and progressions. The syntax is designed to be simple and efficient.

For managing large multi-week programs, Liftoscript offers powerful ways to repeat exercises across multiple weeks, reuse exercises, override some reused parts, reuse `progress` and `update` blocks, etc.

For complex progressions where we need to remember some state across multiple workouts it offers `state variables`, which would be used to store additional meta info.

The syntax is pretty similar to how people already often describe their programs, inspired by Markdown and JavaScript.

## Basics

Each exercise goes on a separate line. It consists of sections separated by a slash (`/`). First goes the exercise name, and then in any order - the sections. The simplest exercise is written like this:

```
Bench Press / 3x8
```

You can do rep ranges too:

```
Bench Press / 3x8-12
```

You can list multiple sets, separated by commas, like this:

```
Bench Press / 1x5, 1x3, 1x1, 5x5
```

That would be 8 sets total - first 5 reps, then 3 reps, 1 rep, and then 5 sets of 5 reps.

If you don't specify the weight and RPE, it'll keep the weight empty during workout, so user would have to specify it themselves to finish a set. If the set specified the RPE though - it'll infer the weight calculated from RPE tables.

For example if you do:

```
Bench Press / 3x12 @8
```

It'll check in the RPE table that for if you want to do 12 reps per @8 RPE, and probably should use 60% of 1RM.

You can also specify the weight explicitly in kg/lb, like this:

```
Bench Press / 3x12 60kg
```

or specify the weight in 1RM%, like

```
Bench Press / 3x12 70%
```

RPE, percentage and weight can be specified for each set or range of sets individually, so you can mix and match:

```
Bench Press / 1x5 @8, 1x3 @9, 1x1 @10, 5x5 50%
```

This per-set RPE notation is commonly used in professional programs where each set ramps in intensity:

```
Lying Leg Curl / 1x6-8 @9, 1x6-8 @10 / 60s
Squat / 1x6-8 @7, 1x6-8 @8 / 180s
```

You can also add set labels in parentheses to annotate the purpose of each set:

```
Lying Leg Curl / 1x6-8 @10 (Full ROM), 1x6-8 @10 (Full ROM), 1x1+ (Partial) / 60s
T Bar Row / 1x8-10 @9, 1x8-10 @10, 2x1+ (Dropset) / 120s
```

You can specify the rest time. E.g. this is how you could do **myo-reps** - i.e. doing heavy 12, and then doing 5x5 with short rest times and same weight:

```
Bench Press / 1x12 20s 60%, 5x5 20s 60%
```

You can also specify the rest time, weight, 1RM percentage and RPE also, for all sets, so you don't have to repeat yourself. Do it in a separate section like this:

```
Bench Press / 1x12, 5x5 / 20s 60%
```

To add AMRAP sets, add `+` after the reps number. And to log RPE, add `+` after the RPE number. Like this:

```
Bench Press / 4x5, 1x5+ @8+
```

And if you want the app to ask you what was the weight you did (similar to AMRAP reps), you can add `+` after the weight:

```
Bench Press / 3x8 / 100lb+
```

or

```
Bench Press / 1x6 70%+, 5x5 50%
```

### Full mode, weeks and days

There's a way to switch to the "Full Mode", where your whole program is just one blob of text. There, to specify different weeks/days, you use this syntax:

```
# Week 1
## Day 1
Squat / 5x5 / progress: lp(5lb)

## Day 2
Squat / 3x8

# Week 2
## Day 1
Squat / 5x4
```

I.e. prefixing week names with `#`, and day names with `##`.

### Exercise Labels

If you want the same exercises to be separate (e.g. you have Squat as a main lift, and Squat as an accessory lift, and
you want to apply different progressions for them), you can mark exercises with different labels. Like this:

```
# Week 1
## Day 1
main: Squat / 5x5 / progress: lp(5lb)

# Week 2
## Day 1
accessory: Squat / 3x8 / progress: dp(5lb, 8, 12)
```

### Warmups

By default, it will add some warmups, but if you want to change that, you can use `warmup` section, like this:

```
Squat / 5x5 / warmup: 1x5 45lb, 1x5 135lb, 1x3 80%
```

If you don't want warmups at all, you can specify `warmup: none`:

```
Squat / 5x5 / warmup: none
```

### Progressive overload

There are 3 built-in types of progressive overload:

- Linear Progression (**lp**) - increase or decrease the weight by a fixed amount or percentage after N attempts.
- Double Progression (**dp**) - increase the reps within a range, then reset the reps and increase the weight.
- Reps Sum (**sum**) - increase the weight if the total sum of reps of all sets more than the threshold.

You can add a progression like this:

```
Bench Press / 3x8 / progress: lp(5lb)
```

You only need to add it to one of the days in your program per exercise, no need to repeat it week over week or day over day. It will be applied to all such exercises in a program. You may disable progression for specific days or weeks via `progress: none` section. This is essential for **deload weeks** where you want exercises to stay at current weight:

```
// Deload week
# Week 7
## Full Body
Squat / 1x6-8 @7, 1x6-8 @8 / 180s / progress: none
Bench Press / 1x6-8 @8, 1x6-8 @9 / 180s / progress: none
```

If you try to specify different progressions for the same exercise in different weeks/days, it'll give you an error - the progressions are applied for an exercise across whole program. You cannot have e.g. linear progression on day 1, and double progression on day 2.

There's a way to have e.g. 2 Bench Press exercises with different progressions though - you can add labels to exercises, and they would be considered different exercises in that case. Label is just some word before an exercise name, with a colon `:` after it.

#### Linear Progression

```
lp(weight increase, increase attempts, current increase attempt, weight decrease, decrease attempts, current decrease attempt)
```

Examples:
```
Squat / 3x8 / progress: lp(5lb)
Squat / 3x8 / progress: lp(5lb, 2)
Squat / 3x8 / progress: lp(5lb, 2, 1, 10lb, 3)
Squat / 3x8 / progress: lp(5%)
```

#### Double Progression

```
dp(weight increase, min reps, max reps)
```

Examples:
```
Bench Press / 3x8 / progress: dp(5lb, 8, 12)
Bench Press / 3x6 / progress: dp(5%, 6, 10)
```

#### Sum Of Reps Progression

```
sum(reps threshold, weights increase)
```

Example:
```
Bench Press / 3x10+ / progress: sum(30, 5lb)
```

### Ways to make written programs less repetitive

#### Reusing exercises via `...Squat`

You can reuse the sets/reps/weight/RPE/timer and warmups of another exercise:

```
Bench Press / 5x5 / progress: lp(5lb)
Squat / ...Bench Press
```

For multi-week programs:

```
# Week 1
## Day 1
Bench Press / 3x8
Squat / ...Bench Press

# Week 2
## Day 1
Bench Press / 3x9
Squat / ...Bench Press
```

You can specify the exact week/day to reuse from: `...Bench Press[2]` (day 2 current week) or `...Bench Press[2:1]` (week 2, day 1).

You can override anything in the reusing exercise:

```
Squat / 3x8 200lb 60s
Bench Press / ...Squat / 150lb
```

#### Repeating exercises over multiple weeks via `Squat[1-4]`

```
Bench Press[1-5] / 3x8
```

This means Bench Press with 3x8 repeats on weeks 1-5, no need to type it again.

With ordering: `Squat[1,1-4]` means order=1 for weeks 1-4.

#### Exercise templates via `/ used: none`

```
t1 / used: none / 1x10+, 3x10 / 70% / progress: lp(5lb)
Bench Press / ...t1
```

Templates never progress, so they won't break reusing.

#### Combining it all together

```
# Week 1
## Day 1
t1 / used: none / 1x6, 3x3 / 80%
t2 / used: none / 1x8, 3x4 / 70%
t3[1-4] / used: none / 3x10+ / 60% / progress: sum(30, 5lb)

Squat[1,1-4] / ...t1
Romanian Deadlift[2,1-4] / ...t2
Bicep Curl[3,1-4] / ...t3

## Day 2
Bench Press[1,1-4] / ...t1
Overhead Press[2,1-4] / ...t2
Lat Pulldown[3,1-4] / ...t3

# Week 2
## Day 1
t1 / 1x7, 3x4 / 80%
t2 / 1x9, 3x5 / 70%
## Day 2
```

## Advanced

For custom progressions, use `progress: custom()` syntax:

```
Bench Press / 3x8 / progress: custom() {~
  if (completedReps[1] >= reps[1]) {
    weights += 5lb
  }
~}
```

### State Variables

```
Bench Press / 3x8 / progress: custom(attempt: 0) {~
  if (completedReps >= reps) {
    state.attempt += 1
    if (state.attempt > 3) {
      weights += 5lb
      state.attempt = 0
    }
  }
~}
```

Reuse progress logic: `progress: custom(attempt: 0) { ...Bench Press }`

### Set Variations

```
Squat / 5x3 / 6x2 / 10x1 / progress: custom() {~
  if (completedReps >= reps) {
    weights = weights[ns] + 5lb
  } else {
    setVariationIndex += 1
  }
~}
```

### Update

```
Bench Press / 3x8 / update: custom() {~
  if (setIndex == 1 && completedReps[1] >= reps[1]) {
    numberOfSets = 4
    sets(2, 4, floor(reps[1] / 2), floor(reps[1] / 2), 0, weights[1], 0, 0)
  }
~}
```

### Tags

```
Squat / 3x8 / id: tags(1, 100) / progress: custom(rating: 0) {~ ~}
Overhead Press / 3x8 / progress: custom() {~
  state[1].rating = 10
~}
```

### Split exercise lines

```
Squat / 1x5 @8 75% 120s, 3x8 @9 60s \
  / warmup: 1x5, 1x3, 1x1 \
  / progress: lp(5lb)
```

## Built-in functions

- `rpeMultiplier(reps, rpe)` - RPE multiplier of 1RM
- `floor(n)`, `ceil(n)`, `round(n)` - rounding
- `sum(array)`, `min(array)`, `max(array)` - aggregation
- `increment(weight)`, `decrement(weight)` - equipment-based weight change
- `sets(fromIndex, toIndex, minReps, maxReps, isAmrap, weight, timer, rpe, shouldLogRpe)` - set builder (update only)


# List of all the built-in exercises

Those exercises are available in the app by default, prefer to use them if possible when you build a program:

Ab Wheel
Arnold Press
Arnold Press, Kettlebell
Around The World
Back Extension, Bodyweight
Back Extension
Ball Slams
Battle Ropes
Behind The Neck Press
Behind The Neck Press, Smith Machine
Behind The Neck Press, Band
Bench Dip
Bench Press
Bench Press, Cable
Bench Press, Dumbbell
Bench Press, Smith Machine
Bench Press, Band
Bench Press, Kettlebell
Bench Press Close Grip
Bench Press Close Grip, Smith Machine
Bench Press Close Grip, EZ Bar
Bench Press Wide Grip
Bench Press Wide Grip, Smith Machine
Bent Over One Arm Row
Bent Over Row
Bent Over Row, Cable
Bent Over Row, Dumbbell
Bent Over Row, Smith Machine
Bent Over Row, Band
Bent Over Row, Leverage Machine
Bicep Curl, Barbell
Bicep Curl, Cable
Bicep Curl
Bicep Curl, Band
Bicep Curl, Leverage Machine
Bicep Curl, EZ Bar
Bicycle Crunch
Box Squat
Box Squat, Dumbbell
Bulgarian Split Squat
Cable Crossover
Cable Crunch
Cable Kickback
Cable Pull Through
Cable Twist, Barbell
Cable Twist
Cable Twist, Band
Cable Twist, Bodyweight
Cable Twist, Leverage Machine
Calf Press on Leg Press
Calf Press on Seated Leg Press
Chest Dip
Chest Fly, Barbell
Chest Fly, Cable
Chest Fly
Chest Fly, Leverage Machine
Chest Press, Band
Chest Press, Leverage Machine
Chin Up
Chin Up, Leverage Machine
Clean
Clean and Jerk
Concentration Curl, Barbell
Concentration Curl, Cable
Concentration Curl
Concentration Curl, Band
Cross Body Crunch
Crunch, Cable
Crunch
Crunch, Leverage Machine
Deadlift
Deadlift, Cable
Deadlift, Dumbbell
Deadlift, Smith Machine
Deadlift, Band
Deadlift, Kettlebell
Deadlift, Leverage Machine
Deadlift High Pull
Decline Bench Press, Dumbbell
Decline Bench Press, Smith Machine
Deficit Deadlift
Deficit Deadlift, Trap Bar
Elliptical Machine
Face Pull
Flat Knee Raise
Flat Leg Raise
Front Raise, Barbell
Front Raise, Cable
Front Raise
Front Raise, Band
Front Raise, Bodyweight
Front Squat
Front Squat, Cable
Front Squat, Dumbbell
Front Squat, Smith Machine
Front Squat, Kettlebell
Goblet Squat
Goblet Squat, Kettlebell
Good Morning
Good Morning, Smith Machine
Good Morning, Leverage Machine
Glute Bridge, Barbell
Glute Bridge
Glute Bridge, Band
Glute Bridge March
Glute Kickback
Glute Kickback, Band
Hack Squat
Hack Squat, Smith Machine
Hammer Curl, Cable
Hammer Curl
Hammer Curl, Band
Handstand Push Up
Hang Clean, Kettlebell
Hanging Leg Raise, Cable
Hanging Leg Raise
High Row, Cable
High Row
Hip Abductor, Cable
Hip Abductor, Band
Hip Abductor, Bodyweight
Hip Abductor
Hip Adductor
Hip Thrust
Hip Thrust, Band
Hip Thrust, Bodyweight
Hip Thrust, Leverage Machine
Incline Bench Press
Incline Bench Press, Cable
Incline Bench Press, Dumbbell
Incline Bench Press, Smith Machine
Incline Bench Press Wide Grip
Incline Chest Fly, Cable
Incline Chest Fly
Incline Chest Press
Incline Chest Press, Band
Incline Chest Press, Leverage Machine
Incline Curl
Incline Row, Barbell
Incline Row
Inverted Row
Jackknife Sit Up
Jump Squat
Jump Squat, Bodyweight
Kettlebell Swing, Dumbbell
Kettlebell Swing
Kneeling Pulldown
Knees to Elbows
Lat Pulldown
Lat Pulldown, Leverage Machine
Lateral Raise, Cable
Lateral Raise
Lateral Raise, Band
Lateral Raise, Kettlebell
Lateral Raise, Leverage Machine
Legs Up Bench Press
Leg Extension, Band
Leg Extension
Leg Press, Smith Machine
Leg Press
Lunge
Lunge, Cable
Lunge, Dumbbell
Lunge, Bodyweight
Lying Bicep Curl, Cable
Lying Bicep Curl
Lying Leg Curl, Band
Lying Leg Curl
Muscle Up
Oblique Crunch
Overhead Press
Overhead Press, Dumbbell
Overhead Press, EZ Bar
Overhead Squat
Overhead Squat, Dumbbell
Pec Deck
Pendlay Row
Pistol Squat, Kettlebell
Pistol Squat
Pistol Squat, Leverage Machine
Plank
Preacher Curl, Barbell
Preacher Curl
Preacher Curl, Leverage Machine
Preacher Curl, EZ Bar
Pull Up, Band
Pull Up
Pull Up, Leverage Machine
Pullover, Barbell
Pullover
Push Press, Barbell
Push Press, Dumbbell
Push Press
Push Press, Bodyweight
Push Up, Band
Push Up
Reverse Crunch, Cable
Reverse Crunch
Reverse Curl, Barbell
Reverse Curl, Cable
Reverse Curl
Reverse Curl, Band
Reverse Fly
Reverse Fly, Band
Reverse Fly, Leverage Machine
Reverse Lunge, Barbell
Reverse Lunge
Reverse Lunge, Kettlebell
Reverse Lunge, Bodyweight
Reverse Wrist Curl
Reverse Wrist Curl, Dumbbell
Reverse Wrist Curl, EZ Bar
Romanian Deadlift, Barbell
Romanian Deadlift
Reverse Hyperextension
Reverse Hyperextension, Leverage Machine
Russian Twist, Cable
Russian Twist, Dumbbell
Russian Twist
Safety Squat Bar Squat
Seated Calf Raise
Seated Calf Raise, Dumbbell
Seated Calf Raise, Leverage Machine
Seated Front Raise, Barbell
Seated Front Raise
Seated Leg Curl
Seated Leg Press
Seated Overhead Press
Seated Palms Up Wrist Curl
Seated Row
Seated Row, Band
Seated Row, Leverage Machine
Seated Wide Grip Row
Shoulder Press, Cable
Shoulder Press
Shoulder Press, Smith Machine
Shoulder Press, Band
Shoulder Press, Leverage Machine
Shoulder Press Parallel Grip
Shrug, Barbell
Shrug, Cable
Shrug
Shrug, Smith Machine
Shrug, Band
Shrug, Leverage Machine
Side Bend, Cable
Side Bend
Side Bend, Band
Side Crunch, Cable
Side Crunch, Band
Side Crunch
Side Hip Abductor, Barbell
Side Hip Abductor
Side Hip Abductor, Leverage Machine
Side Lying Clam
Side Plank
Single Leg Bridge
Single Leg Deadlift
Single Leg Deadlift, Bodyweight
Single Leg Glute Bridge On Bench
Single Leg Glute Bridge Straight Leg
Single Leg Glute Bridge Bent Knee
Single Leg Hip Thrust, Barbell
Single Leg Hip Thrust
Single Leg Hip Thrust, Leverage Machine
Sissy Squat
Sit Up, Kettlebell
Sit Up
Skullcrusher, Barbell
Skullcrusher, Cable
Skullcrusher, Dumbbell
Skullcrusher
Snatch
Split Squat, Barbell
Split Squat
Split Squat, Band
Split Squat, Kettlebell
Split Squat, Bodyweight
Squat
Squat, Dumbbell
Squat, Smith Machine
Squat, Bodyweight
Squat, Leverage Machine
Squat Row
Standing Calf Raise, Barbell
Standing Calf Raise, Cable
Standing Calf Raise
Standing Calf Raise, Bodyweight
Standing Calf Raise, Leverage Machine
Standing Row
Standing Row Close Grip
Standing Row Rear Delt With Rope
Standing Row Rear Delt, Horizontal, With Rope
Standing Row V-Bar
Step up, Barbell
Step up
Step up, Band
Step up, Bodyweight
Stiff Leg Deadlift
Stiff Leg Deadlift, Dumbbell
Stiff Leg Deadlift, Band
Straight Leg Deadlift
Straight Leg Deadlift, Dumbbell
Straight Leg Deadlift, Band
Straight Leg Deadlift, Kettlebell
Sumo Deadlift
Sumo Deadlift High Pull
Superman, Dumbbell
Superman
T Bar Row
Thruster
Toes To Bar
Trap Bar Deadlift
Triceps Dip
Triceps Dip, Leverage Machine
Triceps Extension, Barbell
Triceps Extension, Cable
Triceps Extension
Triceps Extension, Band
Triceps Pushdown
Upright Row, Barbell
Upright Row, Cable
Upright Row
Upright Row, Band
V Up, Dumbbell
V Up, Band
V Up
Wide Pull Up
Wrist Curl
Wrist Curl, Dumbbell
Wrist Curl, EZ Bar
Wrist Roller
Zercher Squat


# Liftoscript Examples

## Basic Beginner Program

```
# Week 1
## Workout A
Bent Over Row / 2x5, 1x5+ / 95lb / progress: lp(2.5lb, 1, 0, 10%, 1, 0)
Bench Press / 2x5, 1x5+ / 45lb / progress: lp(2.5lb, 1, 0, 10%, 1, 0)
Squat / 2x5, 1x5+ / 45lb / progress: lp(5lb, 1, 0, 10%, 1, 0)

## Workout B
Chin Up / 2x5, 1x5+ / 0lb / progress: lp(2.5lb, 1, 0, 10%, 1, 0)
Overhead Press / 2x5, 1x5+ / 45lb / progress: lp(2.5lb, 1, 0, 10%, 1, 0)
Deadlift / 2x5, 1x5+ / 95lb / progress: lp(5lb, 1, 0, 10%, 1, 0)
```

## 5/3/1 for beginners

Uses templates and reuse syntax:

```
# Week 1
## Day 1
main / used: none / 1x5 58%, 1x5 67%, 1x5+ 76%, 5x5 58% / progress: custom(increment: 10lb) {~
  if (dayInWeek > 1 && week == 3) {
    rm1 += state.increment
  }
~}

Squat[1-3] / ...main
Bench Press[1-3] / ...main / progress: custom(increment: 5lb) { ...main }
Hanging Leg Raise[1-3] / 5x10 0lb
Chin Up[1-3] / 5x10 0lb
Push Up[1-3] / 5x15 0lb

## Day 2
Deadlift[1-3] / ...main
Overhead Press[1-3] / ...main / progress: custom(increment: 5lb) { ...main }

## Day 3
Bench Press[1-3] / ...main
Squat[1-3] / ...main

# Week 2
## Day 1
main / 1x3 63%, 1x3 72%, 1x3+ 81%, 5x5 63%
## Day 2
## Day 3

# Week 3
## Day 1
main / 1x5 67%, 1x3 76%, 1x1+ 85%, 5x5 67%
## Day 2
## Day 3
```

## GZCLP Example (with set variations)

```
# Week 1
## Day 1
t1 / used: none / 4x3, 1x3+ / 5x2, 1x2+ / 9x1, 1x1+ / 1x5 (5RM Test) / 75% / progress: custom(increase: 10lb) {~
  if (descriptionIndex == 1) {
    descriptionIndex = 2
  }
  if (setVariationIndex == 4) {
    descriptionIndex = 2
    setVariationIndex = 1
    weights = completedWeights[1] * 0.85
    rm1 = completedWeights[1] / rpeMultiplier(5, 10)
  } else if (completedReps >= reps) {
    weights = completedWeights[ns] + state.increase
  } else if (setVariationIndex == 3) {
    descriptionIndex = 3
    setVariationIndex += 1
  } else {
    setVariationIndex += 1
  }
~}

t2 / used: none / 3x10 / 3x8 / 3x6 / 62% / progress: custom(stage1weight: 0lb, increase: 5lb, stage3increase: 10lb) {~
  if (completedReps >= reps) {
    weights = completedWeights[ns] + state.increase
  } else if (setVariationIndex == 1) {
    state.stage1weight = completedWeights[ns]
    setVariationIndex += 1
  } else if (setVariationIndex == 2) {
    setVariationIndex += 1
  } else {
    setVariationIndex = 1
    weights = state.stage1weight + state.stage3increase
  }
~}

t3 / used: none / 2x15, 1x15+ / 60% 90s / progress: custom() {~
  if (completedReps[ns] >= 25) {
    weights = completedWeights[ns] + 5lb
  }
~}

t1: Squat / ...t1
t2: Bench Press / ...t2
t3: Lat Pulldown / ...t3

## Day 2
t1: Overhead Press / ...t1 / progress: custom(increase: 5lb) { ...t1 }
t2: Deadlift / ...t2 / progress: custom(increase: 10lb, stage3increase: 15lb) { ...t2 }
t3: Bent Over Row / ...t3
```


## Professional Multi-Phase Program (RPE-based with intensification techniques)

This example shows a 12-week program with intro phase (weeks 1-6), deload (week 7), and intensification phase (weeks 8-12) using custom progression templates, per-set RPE, rest times, rich exercise comments, week ranges, dropsets, myo-reps, and lengthened partials:

```
# Week 1
// Intro phase
## Full Body
progression / used: none / 0x1 0lb / progress: custom(lastWeight: 0lb, incr: 5lb) {~
  if (originalWeights[ns] == 0lb) {
    weights = completedWeights[ns]
  }
  var.isCompleted = programNumberOfSets == 1 ?
    completedReps[1] >= reps[1] :
    completedReps[1] >= reps[1] && completedReps[2] >= reps[2]
  if (var.isCompleted) {
    var.lastSetWeight = originalWeights[ns] == 0lb ? completedWeights[ns] : weights[ns]
    state.lastWeight = var.lastSetWeight
    weights = var.lastSetWeight + state.incr
  } else if (state.lastWeight != 0 && min(completedReps) < minReps) {
    weights = state.lastWeight
    reps += 2
  }
~}

dropsets / used: none / update: custom() {~
  if (week >= 8) {
    if (setIndex == 0) {
      weights[programNumberOfSets] = weights[programNumberOfSets - 2] * 0.75
      weights[programNumberOfSets - 1] = weights[programNumberOfSets - 2] * 0.75
    } else if (setIndex == programNumberOfSets - 2) {
      weights[programNumberOfSets] = completedWeights[programNumberOfSets - 2] * 0.75
      weights[programNumberOfSets - 1] = completedWeights[programNumberOfSets - 2] * 0.75
    }
  }
~}

myoreps / used: none / update: custom() {~
  if (week >= 8) {
    if (setIndex == numberOfSets) {
      if (completedReps[numberOfSets] > 1) {
        numberOfSets += 1
        sets(numberOfSets, numberOfSets, 2, 2, 0, weights[numberOfSets], 5, 0, 0)
      }
    }
  }
~}

// [Video](https://youtu.be/y28L1m1PYUQ)
//
// **OG**: Lying Leg Curl > Subs: Seated Leg Curl, Nordic Ham Curl
//
// **Note**: Set the machine so that you get the biggest stretch possible at the bottom.
//
Lying Leg Curl / 1x6-8 @9, 1x6-8 @10 / 60s / progress: custom() { ...progression }

// **OG**: Squat (Your Choice) > Subs: Front Squat, Hack Squat
//
// **Note**: This can be a Barbell Back Squat, Front Squat, or Hack Squat.
Squat / 1x6-8 @7, 1x6-8 @8 / 180s / progress: custom() { ...progression }

// **OG**: Barbell Incline Press > Subs: Smith Machine Incline Press, DB Incline Press
//
// **Note**: Pause for 1 second at the bottom of each rep.
Incline Bench Press / 1x6-8 @8, 1x6-8 @9 / 180s / progress: custom() { ...progression }

Lateral Raise / 1x8-10 @10 / 60s / progress: custom() { ...progression }

Wide Pull Up / 1x6-8 @8, 1x6-8 @9 / 120s / progress: custom() { ...progression }

A: Standing Calf Raise / 1x6-8 @10 / 60s / progress: custom() { ...progression }

## Upper
Lat Pulldown / 1x8-10 @8, 1x8-10 @9 / 120s / progress: custom() { ...progression }
T Bar Row / 1x8-10 @8, 1x8-10 @9 / 120s / progress: custom() { ...progression } / update: custom() { ...dropsets }
Shrug / 1x6-8 @9 / 60s / progress: custom() { ...progression }
Chest Press, Leverage Machine / 1x8-10 @8, 1x8-10 @9 / 180s / progress: custom() { ...progression }
Lateral Raise, Cable / 1x8-10 @9, 1x8-10 @10 / 60s / progress: custom() { ...progression }
Reverse Fly / 1x8-10 @10 / 60s / progress: custom() { ...progression }
Crunch, Cable / 1x6-8 @9, 1x6-8 @10 / 60s / progress: custom() { ...progression }

# Week 2
## Full Body
Lying Leg Curl[2-6] / 1x6-8 @10, 1x6-8 @10 / 60s
Squat[2-6] / 1x6-8 @9, 1x6-8 @10 / 180s
Incline Bench Press[2-6] / 1x6-8 @9, 1x6-8 @10
Lateral Raise[2-6] / 1x8-10 @10 / 60s
Wide Pull Up[2-6] / 1x6-8 @9, 1x6-8 @10 / 120s
A: Standing Calf Raise[2-6] / 1x6-8 @10 / 60s

## Upper
Lat Pulldown[2-6] / 1x8-10 @9, 1x8-10 @10 / 120s
T Bar Row[2-6] / 1x8-10 @9, 1x8-10 @10 / 120s
Shrug[2-6] / 1x6-8 @10 / 60s
Chest Press, Leverage Machine[2-6] / 1x8-10 @9, 1x8-10 @10 / 180s
Lateral Raise, Cable[2-6] / 1x8-10 @10, 1x8-10 @10 / 60s
Reverse Fly[2-6] / 1x8-10 @10 / 60s
Crunch, Cable[2-6] / 1x6-8 @10, 1x6-8 @10 / 60s

# Week 3
## Full Body


## Upper



# Week 4
## Full Body


## Upper



# Week 5
## Full Body


## Upper



# Week 6
## Full Body


## Upper



// Deload week
# Week 7
## Full Body
Lying Leg Curl / 1x6-8 @9, 1x6-8 @10 / 60s / progress: none
Squat / 1x6-8 @7, 1x6-8 @8 / 180s / progress: none
Incline Bench Press / 1x6-8 @8, 1x6-8 @9 / 180s / progress: none
Lateral Raise / 1x8-10 @10 / 60s / progress: none
Wide Pull Up / 1x6-8 @8, 1x6-8 @9 / 120s / progress: none
A: Standing Calf Raise / 1x6-8 @10 / 60s / progress: none

## Upper
Lat Pulldown / 1x8-10 @8, 1x8-10 @9 / 120s / progress: none
T Bar Row / 1x8-10 @8, 1x8-10 @9 / 120s / progress: none
Shrug / 1x6-8 @9 / 60s / progress: none
Chest Press, Leverage Machine / 1x8-10 @8, 1x8-10 @9 / 180s / progress: none
Lateral Raise, Cable / 1x8-10 @9, 1x8-10 @10 / 60s / progress: none
Reverse Fly / 1x8-10 @10 / 60s / progress: none
Crunch, Cable / 1x6-8 @9, 1x6-8 @10 / 60s / progress: none

# Week 8
## Full Body
// **LSIT**: Lengthened Partials (Extend Set)
Lying Leg Curl[8-12] / 1x6-8 @10 (Full ROM), 1x6-8 @10 (Full ROM), 1x1+ (Partial) / 60s / progress: custom() { ...progression }
Squat[8-12] / 1x6-8 @9, 1x6-8 @10 / 180s / progress: custom() { ...progression }
Incline Bench Press[8-12] / 1x6-8 @9, 1x6-8 @10 / 180s / progress: custom() { ...progression }
Lateral Raise[8-12] / 1x8-10 @10 / 60s / progress: custom() { ...progression }
// **LSIT**: Lengthened Partials (Extend Set)
Wide Pull Up[8-12] / 1x6-8 @9 (Full ROM), 1x6-8 @10 (Full ROM), 1x1+ (Partial) / 120s / progress: custom() { ...progression }
A: Standing Calf Raise[8-12] / 1x6-8 @10 (Full ROM), 1x1+ (Partial) / 60s / progress: custom() { ...progression }

## Upper
// **LSIT**: Lengthened Partials (Extend Set)
Lat Pulldown[8-12] / 1x8-10 @9 (Full ROM), 1x8-10 @10 (Full ROM), 1x1+ (Partial) / 120s
// **LSIT**: Two Drop Sets (~25% per)
T Bar Row[8-12] / 1x8-10 @9, 1x8-10 @10, 2x1+ (Dropset) / 120s
Shrug[8-12] / 1x6-8 @10 / 60s
Chest Press, Leverage Machine[8-12] / 1x8-10 @9, 1x8-10 @10 / 180s
Lateral Raise, Cable[8-12] / 1x8-10 @10, 1x8-10 @10 / 60s
Reverse Fly[8-12] / 1x8-10 @10 / 60s
Crunch, Cable[8-12] / 1x6-8 @10, 1x6-8 @10 / 60s

# Week 9
## Full Body


## Upper



# Week 10
## Full Body


## Upper



# Week 11
## Full Body


## Upper



# Week 12
## Full Body


## Upper


```

Key patterns in this example:
1. **Templates** (`progression`, `dropsets`, `myoreps`) defined once at the top with `/ used: none`
2. **Template reuse** via `progress: custom() { ...progression }` and `update: custom() { ...dropsets }`
3. **Per-set RPE** without "RPE" prefix: `1x6-8 @9, 1x6-8 @10`
4. **Rest times** as a section: `/ 60s`, `/ 120s`, `/ 180s`
5. **Rich comments** with OG exercise names, substitutions, and coaching notes
6. **Week ranges** `[2-6]` and `[8-12]` for repeating exercises — empty weeks filled by ranges
7. **Deload week** (Week 7) with `progress: none` on all exercises
8. **Set labels** in parentheses: `(Full ROM)`, `(Partial)`, `(Dropset)`
9. **Exercise grouping** with `A:`, `B:` prefixes for supersets
10. **RPE ramping**: Week 1 starts lower (@7-@9), Week 2+ goes to @10, deload resets to Week 1 RPE


# Liftoscript Grammar (Lezer)

@top Program { expression* }

expression { LineComment | TripleLineComment | Week | Day | ExerciseExpression | EmptyExpression }

ExerciseExpression { ExerciseName Repeat? (SectionSeparator ExerciseSection?)* linebreakOrEof }
EmptyExpression { linebreak }

ExerciseName { NonSeparator+ }
ExerciseSets { CurrentVariation? ExerciseSet ("," ExerciseSet)* }
WarmupExerciseSets { (WarmupExerciseSet ("," WarmupExerciseSet)*) }
ExerciseSection { (ExerciseProperty | ExerciseSets | ReuseSectionWithWeekDay | Superset ) ("\\" linebreak)? }
ReuseSectionWithWeekDay { ReuseSection WeekDay? }
ReuseSection { "..." ExerciseName }
ExerciseSet { (Rpe | Timer | SetPart | WeightWithPlus | PercentageWithPlus | SetLabel)+ }
WarmupExerciseSet { (WarmupSetPart | Weight | Percentage)+ }
Superset { SupersetKeyword ":" ExerciseName }
ExerciseProperty { ExercisePropertyName ":" (FunctionExpression | WarmupExerciseSets | None ) }
ExercisePropertyName { Keyword }
None { @specialize<Keyword, "none"> }
CurrentVariation { "!" }
WeekDay { "[" WeekOrDay (":" WeekOrDay)? "]" }
WeekOrDay { (Int | Current) }
Repeat { "[" (Rep | RepRange) ("," (Rep | RepRange))* "]" }

FunctionExpression {
  FunctionName
  ("(" FunctionArgument? ("," FunctionArgument)* ")")?
  (Liftoscript | ReuseLiftoscript)?
}
ReuseLiftoscript { "{" ReuseSection "}" }
FunctionName { Keyword }
FunctionArgument { Number | Weight | Percentage | Rpe | RepRange | KeyValue }
"""
