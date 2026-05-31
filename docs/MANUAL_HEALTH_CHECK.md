# Manual Health Check

Use this checklist before testing unknown boards, analyzing firmware files, or changing the repository structure.

## Repository check

- Confirm the default branch is `master`.
- Confirm `README.md` describes the current project scope.
- Confirm project notes belong in `docs/`.
- Confirm generated reports belong in `reports/`.
- Confirm sample inputs stay local unless they are legally shareable.

## Board bring-up check

Record the following before flashing or changing anything:

- Board name or best guess
- Chip family
- USB port
- Visible markings
- Boot button behavior
- LED behavior
- Serial output
- Driver or port changes noticed by the laptop

## Capture checklist

Save useful evidence before experimenting:

- Screenshot of device manager or port list
- Screenshot or copy of serial terminal output
- Photo of the board top side
- Photo of the board bottom side
- Notes about cable, port, and boot-button sequence

## Recovery notes

For each test session, record:

- Date
- Board tested
- Tool used
- Command or menu action used
- Result
- Error message if any
- Next planned step

This keeps the project from becoming a haunted junk drawer with Wi-Fi.
