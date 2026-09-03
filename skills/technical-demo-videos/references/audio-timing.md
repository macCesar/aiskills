# Narration entrance, exit, and visual timing

Read this before aligning returned narration audio or deciding the final video duration.

## Measure audible speech

Inspect three different values:

1. the audio container duration;
2. the first audible spoken sample;
3. the last audible spoken sample.

Use silence detection as a measurement aid, then associate speech blocks with the known narration paragraphs. Do not assume every detected pause is a paragraph boundary; voices may pause naturally around punctuation or spelled product names.

## Default margins

- Aim for about `0.35 s` of visual lead-in before the first spoken word. A practical range is `0.25–0.50 s` for a short technical video.
- Aim for `1.5 s` of clean visual post-roll after the last spoken word. A range of `1–2 s` is normally appropriate.
- Count existing leading or trailing silence in the returned audio toward those margins. Do not add the same cushion twice.
- Base the final video duration on the last audible speech plus post-roll, not simply on the audio container duration.

Distribute additional visual time across the matching narration beats. Do not hide a duration mismatch by adding one unrelated pause before the command or by holding a source preview longer than its spoken explanation.

Preserve the original narration file. Do not time-stretch it unless the user explicitly requests that treatment. When muxing, do not use `-shortest` if it would cut the final visual margin.

## Align paragraphs as editable blocks

Treat the narration paragraphs and their matching event-log beats as the units of the final edit. A single unedited audio track is acceptable only when those blocks already align naturally.

When they do not:

1. map each approved paragraph to its audible source range and intended visual event;
2. preserve the original audio file and every spoken sample;
3. remove only unnecessary silence between confidently identified paragraph boundaries;
4. position each speech block so its explanation begins with, or slightly anticipates, the corresponding visible action;
5. extend or trim neutral visual holds where appropriate, distributing corrections across the relevant beats;
6. retain natural conversational pauses and the configured lead-in and post-roll;
7. write the source-audio range, final-video range, and matching visual cue into the cue sheet or recording plan.

Never cut based only on generic silence detection. Confirm boundaries against the approved paragraph text, and do not split a spoken sentence or word. If the returned voice merges paragraphs or inserts ambiguous pauses, report the mismatch instead of guessing.
