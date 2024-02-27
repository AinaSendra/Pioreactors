# Pioreactors


## Turbidostat Increase Stress Automation for Pioreactors
This custom dosing automation, named "Turbidostat Increase Stress", is designed for Pioreactors to maintain a specified target optical density (OD) in a culture while gradually increasing the ratio of an alternate media type.

Features
Target OD Maintenance: Automatically adjusts the media in the bioreactor to maintain a user-defined target OD.
Alternate Media Integration: Incrementally increases the proportion of an alternate media in the culture over time.
Dilution Control: Performs dilutions when the OD exceeds the target, with a mix of normal and alternate media.
Calibration Verification: Ensures that necessary pumps (media, waste, alt_media) are calibrated before operation.
User Configuration
Users must specify the following parameters:

target_od: Desired optical density to maintain in the culture.
volume: Volume of media to be pumped in and out for each dilution.
dilutions: Number of dilutions after which the alternate media ratio is increased.
initial_alt_media: Initial proportion of alternate media in the culture.
alt_media_ratio_increase: Increment by which the alternate media ratio is increased post specified dilutions.
Internal Mechanics
Dilution Tracking: Maintains an internal count of dilutions performed.
Alternate Media Ratio Adjustment: Calculates and adjusts the ratio of alternate media based on user inputs.
Execution Logic: Checks OD levels and manages the addition and removal of media based on the calculated requirements. Updates the alternate media ratio after a set number of dilutions.
Safety Cap: Ensures the alternate media ratio does not exceed 100%.
Error Handling
Calibration Checks: Raises a CalibrationError if any required pump is not calibrated, ensuring safe and accurate automation operation.
