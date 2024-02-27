# DRAFT to try to make the script for having a turbidostat automation, in which after diluting the culture 10 times the ratio of alt media/normal media increases



"""
run on the command line with
$ python3 [name of file].py   --> but this is not for background jobs, no? it should be: python your_script.py >/dev/null 2>&1 & disown

Exit with ctrl-c
"""


from pioreactor.automations.dosing.base import DosingAutomationJobContrib
from pioreactor.utils import local_persistant_storage
# from pioreactor.actions.pump import add_alt_media
from pioreactor.exc import CalibrationError


class TurbidostatIncreaseStress(DosingAutomationJobContrib):

    automation_name = "turbidostat_increase_stress"
    published_settings = {
        "target_od": {"datatype": "float", "settable": True, "unit": "od600"},
        "volume": {"datatype": "float", "settable": True, "unit": "mL"}, # How much volume to be used to dilute the culture when target OD is reached
        # but add sth to check that the volume is not too high / higher than limit
        "dilutions": {"datatype": "float", "settable": True}, # How many dilutions are triggered before the ratio of alt_media increases
        "alt_media_ratio_increase": {"datatype":"float", "settable": True}, # How much we want to increase the ratio of alt media/normal media after "dilutions"
    }
                                                # But we start only with normal media (100% and 0 % of alt media) and then we start putting e.g. 5% alt media + 95 % normal media? or how?
                                                # what if we want to start already with some alt media?

    def __init__(self, target_od, volume, dilutions, alt_media_ratio_increase, **kwargs): # Here we add settings we want to accept from the user (same as published settings)
        super().__init__(**kwargs)
        
    # Calibration checks (added from the turbidostat.py example)
        with local_persistant_storage("current_pump_calibration") as cache: # current_pump_calibration is the name of the folder? by default or i have to change sth?
            if "media" not in cache:
                raise CalibrationError("Media pump calibration must be performed first.")
            elif "waste" not in cache:
                raise CalibrationError("Waste pump calibration must be performed first.")
            elif "alt_media" not in cache:
                raise CalibrationError("alt_media pump calibration must be performed first.")
            # these checks are from: https://github.com/Pioreactor/automation-examples/blob/main/dosing/switching_dosing.py
 # From here down it's from documentation
        self.target_od = float(target_od)
        self.volume = float(volume)
        self.dilutions = float(dilutions) 
        self.alt_media_ratio_increase = float(alt_media_ratio_increase) 


    def execute(self):
        if self.latest_od > self.target_od:   # If OD is higher than target then it triggers to pump in "volume" mL of fresh media and same mL to waste
            self.execute_io_action(media_ml=self.volume, waste_ml=self.volume) # but this triggers only the normal media pump, how do we trigger the alt media pump?
        # count the times this is triggered
        # when count = dilutions variable
            # trigger change in media_ratio variable
        # update this ratio
        # nex times pumps are triggered, the updated ratio is applied




if __name__ =="__main__":
    from pioreactor.background_jobs.dosing_control import DosingController

    dc = DosingController(
        unit="test_unit",               # do i need this? it's for the name of the reactor??
        experiment="test_experiment",
        automation_name="turbidostat_increase_stress", # name of the automation
        duration=1,                     # how often 'execute' runs, in minutes. Check every 1 minute.
        target_od=2.0,                   # kwarg that the turbidostat automation needs
    )
    dc.block_until_disconnected()
