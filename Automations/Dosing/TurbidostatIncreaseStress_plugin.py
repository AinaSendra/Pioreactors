

from pioreactor.automations.dosing.base import DosingAutomationJobContrib
from pioreactor.utils import local_persistant_storage
from pioreactor.exc import CalibrationError
from pioreactor.background_jobs.dosing_control import DosingController


__plugin_summary__ = "Dosing automation for maintaining target OD with increasing alternate media ratio"
__plugin_version__ = "0.0.1"
__plugin_name__ = "Turbidostat Increase Stress"
__plugin_author__ = "Aina Sendra Ortiz"
#__plugin_homepage__ = "https://docs.pioreactor.com"



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
    # Check if the latest OD reading is available
    if is_job_running(ODReading.job_name, unit=self.unit, experiment=self.experiment):
        latest_od = self.latest_od.get('2')  # 2 is the channel for OD readings

        if (latest_od is not None) and (latest_od > self.target_od):
            self.dilution_count += 1
            alt_media_ml = self.volume * self.alt_media_ratio # This calculates the volume of alternate media to add based on the current alt_media_ratio.
            media_ml = self.volume - alt_media_ml              # This calculates the remaining volume to be filled with normal media.
            self.execute_io_action(media_ml=media_ml, alt_media_ml=alt_media_ml, waste_ml=self.volume) #  This line triggers the action to add the calculated volumes of normal and alternate media and remove an equal amount as waste.

            if self.dilution_count >= self.dilutions:
                self.update_media_ratio() # If true, update_media_ratio method is called to update the ratio of alternate media
                self.dilution_count = 0 # Reset the count for the next cycle
    else:
        self.logger.warning("OD Reading job is not running. Latest OD data is not available.")
   

    def update_media_ratio(self):
        self.alt_media_ratio += self.alt_media_ratio_increase
        self.alt_media_ratio = min(self.alt_media_ratio, 1.0)  # Ensure it doesn't exceed 100%



