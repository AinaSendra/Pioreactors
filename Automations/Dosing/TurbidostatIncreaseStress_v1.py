"""
run on the command line with
'nohup python3 your_script.py &'

Exit with ctrl-c
"""



from pioreactor.automations.dosing.base import DosingAutomationJobContrib
from pioreactor.utils import local_persistant_storage
from pioreactor.exc import CalibrationError


class TurbidostatIncreaseStress(DosingAutomationJobContrib):
    automation_name = "turbidostat_increase_stress"
    published_settings = {
        "target_od": {"datatype": "float", "settable": True, "unit": "od600"},
        "volume": {"datatype": "float", "settable": True, "unit": "mL"},
        "dilutions": {"datatype": "int", "settable": True},
        "initial_alt_media": {"datatype": "float", "settable": True},  # The initial proportion of alt_media, so for ex. 0.05 if we want 5% alt_media and 95% normal media
        "alt_media_ratio_increase": {"datatype":"float", "settable": True}, # If we want the alt_media to increase by 5% then we input here 0.05
    }

    def __init__(self, target_od, volume, dilutions, initial_alt_media, alt_media_ratio_increase, **kwargs):
        super().__init__(**kwargs)

        self.target_od = float(target_od)
        self.volume = float(volume)
        self.dilutions = int(dilutions)
        self.initial_alt_media= float(initial_alt_media)  
        self.alt_media_ratio_increase = float(alt_media_ratio_increase)
        self.dilution_count = 0 # this is an internal parameter, not input by user, so not an argument in the __init__ method
        
        self.alt_media_ratio = self.initial_alt_media  # Set the initial alt_media_ratio


        # Calibration checks
        self.check_calibration(["media", "waste", "alt_media"])  # This is a call to the check_calibration method, and if you add that list it performs the calibration check for each of those pumps.

    def check_calibration(self, pumps):     # It checks each pump listed in the provided array against the calibration cache.
                                            # It contains the logic for checking the calibration status. 
                                            # This method takes a list of pumps as its argument, iterates over this list, and checks if each pump is present in the calibration cache. 
                                            # If a pump is not calibrated, it raises a CalibrationError.
        with local_persistant_storage("current_pump_calibration") as cache:
            for pump in pumps:
                if pump not in cache:
                    raise CalibrationError(f"{pump} pump calibration must be performed first.")

    def execute(self):
        if self.latest_od['2'] > self.target_od:
            self.dilution_count += 1
            alt_media_ml = self.volume * self.alt_media_ratio # check this
            media_ml = self.volume - alt_media_ml              # check this
            self.execute_io_action(media_ml=media_ml, alt_media_ml=alt_media_ml, waste_ml=self.volume)

            if self.dilution_count >= self.dilutions:
                self.update_media_ratio()
                self.dilution_count = 0

    def update_media_ratio(self):
        self.alt_media_ratio += self.alt_media_ratio_increase
        self.alt_media_ratio = min(self.alt_media_ratio, 1.0)  # Ensure it doesn't exceed 100%

if __name__ == "__main__":
    from pioreactor.background_jobs.dosing_control import DosingController # To import the DosingController class, responsible for managing dosing automation in the Pioreactor.
# This is for creating an instance of DosingController, initializing with specific parameters.
# This is for testing purposes, to show how the automation can be initialized and run with specific parameters. 
# But ideally we want users to input these parameters, so this section would be modified to gather user inputs (through the UI probably)
    dc = DosingController(
        automation_name="turbidostat_increase_stress",
        target_od=2.0,
        volume=1.0,
        dilutions=10,
        initial_alt_media=0.0,
        alt_media_ratio_increase=0.05,
        # Additional kwargs...
    )
    dc.block_until_disconnected() # To run the dosing automation continuously until interrupted




'''
To modify your script so that it takes input values for the variables from the user (rather than having them hardcoded in the script), you would need to implement a way to gather user input. This could be done in several ways depending on how the script is being used:

1) Command Line Arguments: Use Python's argparse module to allow users to pass values as command-line arguments. This is suitable for users comfortable with command-line interfaces.

2) Interactive Input: Use Python's input() function to prompt the user for input when the script runs. This method is straightforward but requires the script to be run in an interactive environment.

3) User Interface (UI): If the Pioreactor software has a UI, you could integrate your script with the UI to accept input. This would require more complex integration with the Pioreactor system and its UI framework.

4) Configuration File: Read the parameters from a configuration file that the user can edit. This allows users to set their parameters in a file, which your script reads upon execution.

'''