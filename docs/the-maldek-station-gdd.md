# THE MALDEK STATION

**A cable car horror game about routine, isolation, and the things that come back from the mountain.**

---

**Status:** Concept / Pre-Production
**Version:** 0.1
**Date:** February 2026

---

## 1. Concept Overview

**The Maldek Station** is a first-person psychological horror game in which the player takes on the role of a cable car operator working a solo night shift at a remote alpine station. The core mechanic is a repeating operational loop: send the gondola up the mountain, wait, receive it when it returns, inspect it, maintain the station systems, and send it again. The game's horror emerges when the car begins returning with evidence that something at the unmanned Maldek station is interacting with it.

The design philosophy is constraint-driven, inspired by P.T. (Silent Hills). A small, meticulously detailed environment repeated through a loop structure creates deep player familiarity, which is then systematically violated. The entire game takes place at Millford station, approximately 30 square meters in size. The player never visits Maldek. The mountain, the cable, and the returning gondola are the delivery mechanism for all horror.

The game spans five nights of increasingly disturbing shifts, with each night consisting of 3 to 4 cable car cycles lasting roughly 15 to 20 minutes of real time. Total playtime is approximately 90 minutes.

---

## 2. Setting & Premise

### 2.1 The World

A remote alpine cable car line connecting Millford station in the valley to Maldek station on the mountain ridge. The setting is mid-century European alpine infrastructure: concrete, timber, heavy steel cable mechanisms, analog instrumentation. The time period is deliberately ambiguous but the technology is mechanical and analog rather than digital. The mountain is forested with dense pine, prone to fog, and at altitude where weather shifts rapidly.

### 2.2 Millford Station (Lower)

The player's entire world. A small functional building at the base of the cable line comprising four zones: a control room (the player's home base with the operating console and desk), a platform (the open-air concrete dock where the gondola arrives), a maintenance room (generator, breakers, tools, the previous operator's locker), and an overlook (an exposed railing with mounted binoculars aimed up the mountain). The station is surrounded by dark forest on three sides, with the cable line ascending northward into the mountain.

### 2.3 Maldek Station (Upper)

A small unmanned turnaround station on the mountain ridge. Visible from Millford as a distant structure with a single amber light. The player never visits it. Maldek is the source of all mystery and dread. It exists only as a distant point of light, a silhouette through binoculars, and whatever evidence the returning gondola carries back. Its true nature is never fully explained.

### 2.4 Premise and Backstory

The player is a newly hired overnight operator. This is their first solo night shift. The cable car runs automated overnight cycles for mechanical stress testing, which is standard procedure for alpine cable systems. The station also serves as an emergency standby in case a stranded hiker or researcher at Maldek needs evacuation. The previous night operator recently left the position. The reasons are unclear. A handwritten note left on the desk is the first narrative hook.

The justification for why the cable runs at night is layered. The **mechanical answer** is stress testing. The **operational answer** is emergency readiness. The **real answer**, which the player pieces together across five nights, is that something at Maldek wants the car to keep coming, and it has been happening to every operator who has worked this shift.

---

## 3. Core Game Loop

Each cable car cycle follows a seven-step operational loop. The player learns this loop during the first two normal cycles of Night 1. Once internalized, the game disrupts individual steps to create tension, missed information, and forced triage decisions.

### 3.1 The Cycle

1. **Monitor** — Sit in the control room. Watch the panel gauges. Wait for the car to return. Observe the cable, the mountain, the Maldek light through the window.
2. **Receive** — The car docks at the platform. Walk outside. Open the gondola door.
3. **Inspect** — Enter the gondola. Check the benches, windows, floor. Note anything left behind or anything wrong. This is the primary horror discovery point.
4. **Log** — Return to the control room. Write the cycle entry in the logbook. Record any anomalies.
5. **Maintain** — Check the panel for system warnings. Refuel the generator, reset tripped breakers, adjust the cable tensioner, perform any physical repairs. This step pulls the player away from the control room.
6. **Communicate** — Perform the scheduled dispatch radio check-in. Listen for incoming transmissions. Answer the phone if it rings.
7. **Send** — Reset the cycle counter. Pull the drive lever. Send the car back up into the mountain. Watch it disappear.

Between sending and the next arrival, the player has 3 to 4 minutes of real time. This is the tension window: maintenance tasks, optional binocular checks at the overlook, reviewing the logbook, exploring the maintenance room. The game uses this wait to build dread through audio design, subtle environmental shifts, and the simple act of watching the cable move.

### 3.2 Cycle Disruption

The horror engine works by breaking individual steps of the loop:

| Step | Disruption Example |
|------|-------------------|
| Monitor | A gauge reads an impossible value. The cycle counter increments on its own. |
| Receive | The car arrives early, or doesn't open, or you hear it dock while you're in maintenance and can't see it. |
| Inspect | A personal item appears. Condensation on the window. The car smells like a crowd. A scratch on the interior wall. |
| Log | An entry exists that you didn't write. A previous entry has changed. A page is missing. |
| Maintain | Multiple systems fail simultaneously, forcing triage. The generator fuel is draining impossibly fast. A breaker has been flipped by something else. |
| Communicate | Dispatch confirms a cycle you haven't run. The radio transmits your own voice. The phone rings from Maldek. |
| Send | The car begins ascending on its own before you pull the lever. The drive lever won't engage. The cable moves but the car doesn't. |

---

## 4. Station Layout

The station comprises four interconnected zones designed around two principles: every zone has a distinct gameplay function, and every zone has a blind spot to at least one other zone. This ensures the game can place or change things while the player is elsewhere.

### 4.1 Control Room

**Function:** Home base. Information and decisions. This is where the player monitors all station systems and waits for the car. The room is warm, lit by fluorescent tubes, and designed to feel like a cockpit: small, contained, everything within arm's reach. A large window faces the platform and the cable ascending into the mountain.

**Sightlines:** Can see the platform, the cable, and the approaching car through the window. Cannot see the overlook or the maintenance room interior.

**Connections:** Door to the platform (north). Internal door to the maintenance room (east).

### 4.2 Platform

**Function:** Transition zone between safety and exposure. Open-air concrete dock where the gondola arrives. Two overhead industrial lamps create a pool of light; the edges fall into dark forest. The cable wheel mechanism is the dominant feature. This is where the player is most physically vulnerable.

**Sightlines:** Can see the cable ascending, the control room window, and the overlook. Cannot see inside the maintenance room.

**Connections:** Door to the control room (south). Door from the maintenance room (south-east). Open passage to the overlook (east).

### 4.3 Maintenance Room

**Function:** Power and electrical hub. Cold, loud from the generator, industrial. Houses the diesel generator that powers the entire station, the circuit breaker panel that distributes power to all systems, tools and spare parts for physical repairs, and the previous operator's locker. When the player is here they cannot hear subtle sounds and cannot see the control panel or the platform. The game pulls the player here when it wants them blind and deaf.

A rear door on the south wall opens to the outside, where a bulk diesel tank sits on a concrete pad behind the station. The tank is the station's main fuel reserve. The fuel drum inside the maintenance room is the operator's working supply for a single shift. On normal nights it is sufficient. On later nights, when fuel consumption exceeds any reasonable rate, the operator must go outside through the rear door to refuel from the bulk tank — leaving the station entirely, exposed to the dark forest and mountain, while the station above runs unmonitored.

**Sightlines:** Cannot see the platform, the control room panel, or the overlook. Effectively isolated from all information sources. The rear exterior is worse: outside, behind the building, no line of sight to anything.

**Connections:** Stairway up to platform (north). Rear door to exterior fuel area (south). This means the player can be pulled outside and below in a single task chain: stairs down, refuel drum, realize drum isn't enough, open rear door, step outside into the dark.

### 4.4 Overlook

**Function:** Observation point. A railed balcony at the platform's edge with fixed mounted binoculars aimed at Maldek. The most exposed location in the station, lit only by spill from the platform lamps. Using the binoculars locks the player's vision: they cannot see their surroundings while looking. Every visit here is a voluntary choice to trade situational awareness for information about the mountain.

**Sightlines:** Unobstructed view up the mountain. Can see the Maldek light. While using binoculars, the player sees nothing around them.

**Connections:** Open passage to the platform (west). Dead end in all other directions.

### 4.5 The Gondola

Not a station zone but a critical space. When docked, the player enters it to inspect. The gondola is the only object in the game that travels to Maldek and returns. It is an artifact from the other place. The interior is a confined box: two wooden benches, a dome light, rubber floor matting, large windows showing black outside. Each cycle, stepping into the gondola means stepping into a space that was just somewhere the player cannot see or control.

### 4.6 Circulation Principle

The two-path loop is the most important spatial decision. The player can move between the control room and the platform via two routes: directly through the control room door, or indirectly through the maintenance room. This means the game can force the player through the maintenance room (breaker trip, fuel alarm) and deliver them to the platform from an unfamiliar angle. Arriving at a familiar space from an unexpected direction is inherently unsettling.

---

## 5. Subsystems & Mechanics

The station runs on three interdependent subsystems. Each is monitored from the control room panel but repaired elsewhere. This creates the core tension mechanic: leaving the control room to fix things means losing visibility of the platform and the incoming car.

### 5.1 Cable Drive

The mechanical system that moves the gondola. Motor, cable wheel, tensioner, brake. Monitored via analog gauges on the control panel: cable tension, motor temperature, brake pressure, and a mechanical cycle counter.

**Normal maintenance:** Tensioner drifts and needs manual adjustment at the platform cable housing. Motor overheats and requires a breaker reset in the maintenance room. Brake can stick and needs physical release at the platform mechanism.

**Horror application:** The cable moves when no command is sent. The tension gauge shows passenger weight in a car that arrives empty. The cycle counter increments during a cycle that hasn't completed. The brake releases on its own.

### 5.2 Power

A diesel generator in the maintenance room powers the entire station. A fuel gauge on the control panel tracks reserves. A hand pump and fuel drum in the maintenance room handle shift-level refueling. A bulk diesel tank on a concrete pad behind the station (accessible through the maintenance room rear door) holds the station's main fuel reserve. The circuit breaker panel controls distribution to platform lights, interior lights, the control panel, and the radio.

**Normal maintenance:** Generator sputters and needs restart. Breakers trip from power surges and need to be manually flipped. Fuel level drops and needs replenishment from the drum.

**Horror application:** Breakers trip on their own, selectively killing platform lights or the radio. Fuel consumption exceeds any normal rate, as though something else is drawing power. The shift drum runs dry far too early, forcing the player outside to the bulk tank behind the station — alone, in the dark, behind the building with no sightline to the platform or control room. A breaker is found in a position the player didn't leave it in. The generator stops and the silence is worse than any sound.

### 5.3 Communications

A desk radio unit for dispatch check-ins and a landline phone to the operations office. The radio has a signal strength indicator on the panel and a speaker for passive monitoring. The player is expected to check in with dispatch at scheduled intervals.

**Normal operation:** Routine check-ins. Dispatch confirms your reports. The phone is silent.

**Horror application:** Dispatch confirms a cycle you haven't run. The radio receives a transmission on a frequency your equipment shouldn't pick up. The phone rings from Maldek's line, which should be dead. Your dispatch check-in is answered by a voice that is almost yours.

### 5.4 The Degradation Meta-Mechanic

As each night progresses, maintenance tasks become more frequent and more urgent. The generator drinks fuel faster. Breakers trip more often. The tensioner drifts further. The player is pulled away from the control room with increasing frequency, spending more time reacting and less time monitoring. This creates a natural escalation of anxiety separate from any scripted scare: the player is losing control of a system they were responsible for. Eventually they must triage: fix the platform lights or refuel the generator? Answer the radio or inspect the car that just docked unmonitored?

---

## 6. Control Panel & Room Detail

### 6.1 The Control Panel

The panel is entirely analog and mechanical. Heavy switches, not touchscreens. Things clunk when moved. This matters for horror because analog systems fail in physical, tangible ways: a needle drifting, a light dying, a lever that resists. Digital failure is abstract; analog failure is visceral.

**Top Row — Cable System Gauges**

- **Cable tension gauge** — Large analog dial. The most-watched instrument. The player learns what "normal" looks like, which makes abnormal readings deeply unsettling.
- **Motor temperature** — Analog dial with a red zone.
- **Brake pressure** — Analog dial.
- **Cycle counter** — Mechanical flip-number display. Satisfying clack when it increments. Terrifying when it increments on its own.

**Middle Row — Status Indicators**

A row of backlit indicator lights: platform lights, interior lights, generator status, radio link, brake engaged, cable drive active. Green is nominal. Amber is warning. Red is fault. These indicators are the player's early warning system and their first point of dread when a light changes color unexpectedly.

**Bottom Row — Controls**

- **Main drive lever** — Sends or stops the car. Heavy, requires deliberate action.
- **Brake release lever** — Manual override.
- **Emergency stop** — Under a red flip cover. The player may never need it, but its presence is a constant reminder of catastrophic failure.
- **Light switches** — Platform and interior lighting, individually controlled.

### 6.2 The Desk

- **Logbook** — Gameplay prop. The player writes entries each cycle. Reviewing past entries is a core interaction. Entries that appear, change, or vanish are a key horror vector.
- **Radio unit + handset** — Dispatch communication. Built-in speaker for passive monitoring.
- **Landline phone** — Emergency line to operations office. Silent until it isn't.
- **Thermos, pen, desk lamp** — Details that establish normalcy and warmth.
- **Previous operator's note** — First narrative hook. Handwritten, taped to the desk. Its content is ambiguous: possibly helpful, possibly a warning, possibly unhinged.
- **Emergency procedures card** — Laminated. Covers normal failure modes. Critically, it does not cover what the player experiences.
- **Wall checklist** — Functions as a subtle tutorial for the player's first two cycles.
- **Cable line photograph** — Faded image of both Millford and Maldek in daylight. A reminder that this place is supposed to be normal.
- **Coat hook** — High-vis vest and a flashlight. The flashlight is a key gameplay prop grabbed whenever the player exits to the platform.
- **Space heater** — The source of the room's warmth. When it fails, the player feels the cold physically and psychologically.

### 6.3 Analog Design Philosophy

Every piece of information in the game is delivered through physical, in-world objects: analog gauges, handwritten logs, radio static, a distant light on a mountain. There are no HUD elements, no on-screen UI, no floating text. The player's interface is the station itself. This means the horror is always delivered through the same instruments the player relies on for safety, which makes the betrayal of those instruments profoundly destabilizing.

---

## 7. Escalation & Night Structure

The game spans five nights. Each night is a single shift consisting of 3 to 4 cable car cycles, approximately 15 to 20 minutes of real time per night. The hybrid structure provides the compressed tension of a looping game with the slow-burn dread of returning to a workplace that is getting worse.

### Night 1 — Normal

The tutorial night. Everything works as described. The player learns the full cycle loop, becomes familiar with all four zones, understands the panel, performs routine maintenance. The Maldek light is visible and steady. The gondola returns empty and clean. Dispatch check-ins are boring. The night is uneventful. This is essential: the player must internalize what "normal" feels like before it can be violated.

*Between-night beat: The player returns for Night 2. The station is exactly as they left it. Or is it? The thermos has moved. Or maybe it hasn't. The player isn't sure.*

### Night 2 — Doubt

Subtle wrongness. The car takes slightly longer to return than expected. Condensation appears on the gondola window interior. The cable tension gauge flickers once. The Maldek light seems to blink, but the previous operator's note said it's just the bulb cycling. The radio has a moment of static that almost sounds structured. Nothing is definitive. The player is unsure whether they're imagining things.

*Between-night beat: Arriving for Night 3, the logbook has an entry for a cycle that occurred during the day. The day operator's handwriting looks rushed.*

### Night 3 — Wrongness

Undeniable anomalies. The car returns with a personal item on the bench: a scarf, a glove, a single shoe. The cable tension gauge shows weight during descent: passenger weight. The car arrives empty. The Maldek light goes out for an entire cycle and returns. The maintenance room locker contains a new item that wasn't there on Night 2. Dispatch check-in is normal, but the sign-off phrase is different from every previous check-in. A phone rings once. The player answers. Silence, then the line is dead.

*Between-night beat: The player's note on the desk has been moved. Underneath it is a second note, in different handwriting, older: "Don't send it back up."*

### Night 4 — Hostility

The station pushes back. Multiple system failures occur simultaneously, forcing triage. The car arrives and won't open; when forced, it smells like a crowd of people. The cable moves without the player engaging the lever. The gondola returns with the window broken from the inside. A second light appears on the mountain near Maldek, moving. The radio activates with a voice giving operational instructions in a tone that's almost the player's own. The logbook has an entry the player didn't write: "Passenger complained of noise."

*Between-night beat: The player arrives for Night 5. The station door is already unlocked. The interior lights are on. The control panel is active. Someone, or something, has been operating the station.*

### Night 5 — Collapse

The final shift. Systems degrade rapidly. The car goes up and doesn't come back. The cable goes slack, then taut, then slack, as if something is pulling on it from above. When the car returns, it's damaged: dents from the inside, scratches on the walls. Maldek is no longer visible, not because of fog but because there is nothing there. The binoculars show empty mountain where the station should be. But the car still goes up and comes back. The final cycle delivers the endgame.

---

## 8. Horror Design Principles

The following rules govern all horror content in the game. They exist to maintain a consistent tone of psychological dread rather than shock or gore.

### The station never physically changes.

No walls move. No rooms appear. No geometry shifts. The architecture remains trustworthy throughout all five nights. The horror is entirely in the objects, sounds, information, and absences within the space. When something is wrong, the player cannot blame the environment. They must confront that the wrongness is arriving from outside, through the cable, down from the mountain, carried in the car.

### Maldek is never shown up close.

The player never visits Maldek. It exists only as a distant light, a binocular silhouette, and the evidence carried back in the gondola. The moment you show the source, it becomes finite. If you never show it, the player's imagination does work no asset can match. The mountain is a black box. The cable is a thread into the unknown. Every returning car is a message from something that cannot be directly observed.

### Horror is delivered through trusted systems.

The gauges, the logbook, the radio, the dispatch check-ins: these are the player's lifelines. Horror that arrives through these channels is more disturbing than any environmental scare because it corrupts the player's ability to trust their own information. A wrong gauge reading is scarier than a shadow because the gauge is what tells you whether you're safe.

### Player-driven dread over scripted scares.

The binoculars are the purest example. The game never forces the player to look at the mountain. They choose to walk to the most exposed point in the station and lock their vision on Maldek. The dread comes from the player's own decision to seek information, knowing they might see something they cannot undo. Similarly, entering the gondola, opening the logbook, and answering the radio are all voluntary actions. The player scares themselves.

### Sound is the primary horror medium.

The game's audio design carries the majority of the horror: mountain wind, cable hum, generator rumble, distant unidentifiable sounds, the absence of sound. The gondola arriving has a specific mechanical clunk the player learns. When that sound occurs at the wrong time, or doesn't occur when expected, the effect is visceral. Radio static, breathing, a voice that's almost familiar: these are more effective than any visual scare in a game built around waiting in a small room.

### Familiarity is the weapon.

Every horror beat depends on the player knowing what "normal" looks, sounds, and feels like. This is why Night 1 must be completely uneventful and why the seven-step loop must be thoroughly internalized. The horror is not the event itself but the delta between what the player expects and what they get. A needle at the wrong position on a gauge they've watched for an hour is more frightening than a monster they've never seen before.

---

## 9. Narrative Threads

Story is delivered entirely through environmental details and in-world objects. There are no cutscenes, no dialogue trees, and no exposition dumps. The player assembles meaning from fragments found across five nights.

### 9.1 The Previous Operator

The most important narrative thread. Evidence of this person is scattered through the station: the handwritten note on the desk, personal items in the maintenance room locker, entries in the logbook that predate the player's employment. Across five nights, the player pieces together a picture of someone who experienced the same escalation, left fragmented warnings, and eventually stopped coming to work. Whether they quit, disappeared, or are still on the mountain is never confirmed.

### 9.2 The Handwritten Notes

Found in the control room and maintenance room across multiple nights. They contradict each other. The first note is reassuring: the light flickers, the car takes longer sometimes, it's just the equipment. Later notes are less stable. One says "Don't send it back up." Another describes something seen through the binoculars. The handwriting degrades. The last note found may not be from the previous operator at all.

### 9.3 The Gondola Artifacts

Objects found inside the returning gondola across the five nights. Each artifact is a puzzle piece: whose belongings are these? When are they from? A scarf. A glove. An ID badge with no photo. A logbook page from a different station. A child's drawing. These items should never fully resolve into a single coherent story. Multiple interpretations should be possible. The ambiguity is the point.

### 9.4 Radio and Phone Transmissions

Starting from Night 3, the radio and phone deliver narrative fragments: a partial weather report for a date that hasn't happened, a dispatch confirmation for a station that doesn't exist, a voice on the phone that says a single word and hangs up. These transmissions suggest that the cable line connects to something other than a physical station on the mountain. What Maldek really is, is left for the player to infer.

### 9.5 The Logbook

The player's own entries become a narrative element when entries appear that they didn't write, or their previous entries change. The logbook is both a gameplay mechanic and a horror prop. By Night 5, the player may not trust their own documentation, which mirrors the broader theme of a reliable system becoming adversarial.

---

*This document is a living reference and will be updated as development progresses through prototyping, playtesting, and production.*
