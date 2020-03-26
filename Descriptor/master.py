from Descriptor.pipelines import generico
debug = 1
second = 1
minute = 60
hour = 3600
day = 3600 * 24

data_flows = {
    "generico": {
            "descriptor": generico,
            "run_every_seconds": second,
            "initial_hour": 1,
            "final_hour": 24
    }
}
