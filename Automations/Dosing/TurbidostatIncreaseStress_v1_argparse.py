
'''
In order to gather user input for the different parameters, this can be done through: 

1) Command Line Arguments: Use Python's argparse module to allow users to pass values as command-line arguments. This is suitable for users comfortable with command-line interfaces.
'''



import argparse
from pioreactor.automations.dosing.base import DosingAutomationJobContrib
from pioreactor.utils import local_persistant_storage
from pioreactor.exc import CalibrationError
from pioreactor.background_jobs.dosing_control import DosingController



class TurbidostatIncreaseStress(DosingAutomationJobContrib):
    automation_name = "turbidostat_increase_stress"
    published_settings = {
        "target_od": {"datatype": "float", "settable": True, "unit": "od600"},
        "volume": {"datatype": "float", "settable": True, "unit": "mL"}, # Amount pumped in and pumped out for the dilutions (Not culture volume!)
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
        if self.latest_od['2'] > self.target_od: # Check but i think the 2 is bc it's where/which channel is the one reading OD
            self.dilution_count += 1
            alt_media_ml = self.volume * self.alt_media_ratio # This calculates the volume of alternate media to add based on the current alt_media_ratio.
            media_ml = self.volume - alt_media_ml              # This calculates the remaining volume to be filled with normal media.
            self.execute_io_action(media_ml=media_ml, alt_media_ml=alt_media_ml, waste_ml=self.volume) #  This line triggers the action to add the calculated volumes of normal and alternate media and remove an equal amount as waste.

            if self.dilution_count >= self.dilutions:
                self.update_media_ratio() # If true, update_media_ratio method is called to update the ratio of alternate media
                self.dilution_count = 0 # Reset the count for the next cycle

    def update_media_ratio(self):
        self.alt_media_ratio += self.alt_media_ratio_increase
        self.alt_media_ratio = min(self.alt_media_ratio, 1.0)  # Ensure it doesn't exceed 100%

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Turbidostat Increase Stress Automation')
    parser.add_argument('--target_od', type=float, required=True, help='Target optical density')
    parser.add_argument('--volume', type=float, required=True, help='Volume for dilution')
    parser.add_argument('--dilutions', type=int, required=True, help='Number of dilutions')
    parser.add_argument('--initial_alt_media', type=float, required=True, help='Initial alternate media ratio')
    parser.add_argument('--alt_media_ratio_increase', type=float, required=True, help='Media ratio increase after each cycle')

    args = parser.parse_args()

    dc = DosingController(
        automation_name="turbidostat_increase_stress",
        target_od=args.target_od,
        volume=args.volume,
        dilutions=args.dilutions,
        initial_alt_media=args.initial_alt_media,
        alt_media_ratio_increase=args.alt_media_ratio_increase
    )
    dc.block_until_disconnected() # To run the dosing automation continuously until interrupted



'''
To run this script, the user would use a command like:

cd [and the folder where our script is]

nohup python3 your_script.py --target_od 2.0 --volume 1.0 --dilutions 10 --initial_alt_media 0.05 --alt_media_ratio_increase 0.05 &


This allows the user to specify each parameter from the command line when starting the script.
The nohup command allows the script to continue running even if the terminal is closed, and & puts the script in the background, so you can continue using the terminal for other commands.

'''