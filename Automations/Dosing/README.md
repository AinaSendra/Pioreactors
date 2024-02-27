# Turbidostat Increase Stress Automation for Pioreactors


This custom dosing automation, named "Turbidostat Increase Stress", is designed for Pioreactors to maintain a specified target optical density (OD) in a culture while gradually increasing the ratio of an alternate media type.

## Functionality:
* **Maintains Target OD**: It automatically adjusts the media in the bioreactor to maintain a specified target OD.
* **Alternate Media Introduction**: Over time, the automation increases the proportion of the alternate media in the culture.
* **Dilution Process**: When the OD exceeds the target, the system performs a dilution, replacing a portion of the culture with a mix of normal and alternate media.
* **Calibration Checks**: It includes checks to ensure that the necessary pumps (media, waste, alt_media) are calibrated before running.


## User Inputs:
The user must specify the following parameters:

* **'target_od'**: The desired OD to maintain.
* **volume**: The volume of media to be pumped in and out for each dilution.
* **dilutions**: The number of dilutions after which the alternate media ratio is increased.
* **initial_alt_media**: The initial proportion of alternate media in the culture.
* **alt_media_ratio_increase**: The increment by which the proportion of alternate media is increased after the specified number of dilutions.


## Internal Mechanics:
Dilution Count: The system keeps an internal count of dilutions.
Alternate Media Ratio: It calculates and adjusts the ratio of alternate media based on the user-defined parameters.
Execution Logic: The execute method checks if the OD is above the target and, if so, calculates the volumes of normal and alternate media to add and the volume of waste to remove. After a set number of dilutions, it updates the alternate media ratio.
Ratio Cap: The alternate media ratio is capped at 100% to prevent invalid values.


## Error Handling:
Calibration Check: The system raises a CalibrationError if any required pump is not calibrated, ensuring the automation doesn't run with uncalibrated equipment.
In summary, this code enables a controlled and automated process for maintaining a target OD in a bioreactor while experimenting with varying proportions of two different media types, ensuring the process is conducted with properly calibrated equipment.
