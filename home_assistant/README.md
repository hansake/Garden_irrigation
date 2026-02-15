The files here are implementing some Home Assistant automations
to control and supervise the irrigation.

These three automations will turn off the water after
some time.
* Bevattning_dimkylning_växthus_off_after_60_minuter: for fog cooling in the greenhouse
* Bevattning_odlingskragar_off_after_15_minuter: for irrigation in the garden
* Bevattning_växthus_off_after_15_minuter: for irrigation in the greenhouse

These two automation will switch on/off the CubicSecure
water safety unit during irrigation to avoid that it
will detect a leak and turn off the water.
* Bevattning_on_cubicsecure_pause_on: pause CubicSecure when irrigation is ongoing
* Bevattning_off_cubicsecure_pause_off: resume CubicSecure supervision

The CubicSecure integration with Home Assistant is required for this.
* [angoyd/ha-lksystems: Home Assistent component for LK Systems devices.](https://github.com/angoyd/ha-lksystems#readme)
* [Water Safety Unit](https://www.lksystems.se/en/products/lk-water-safety-system/water-safety-unit/)

Sorry for the "swinglish" in these automations.
