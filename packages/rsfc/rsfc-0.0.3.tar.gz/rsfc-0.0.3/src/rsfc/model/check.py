from rsfc.utils import constants

class Check:
    def __init__(self, indicator_id, test_id, process, output, evidence):
        self.checkers_info = constants.CHECKERS_DICT
        
        self.indicator_id = indicator_id
        self.test_id = test_id
        self.process = process
        self.output = output
        self.evidence = evidence

    def convert(self):
        return {
            "@type": "CheckResult",
            "test_id": self.test_id,
            "assessesIndicator": {
                "@id": self.indicator_id
            },
            "checkingSoftware": {
                "@type": "schema:SoftwareApplication",
                "name": self.checkers_info['rsfc']['name'],
                "@id": self.checkers_info['rsfc']['id'],
                "softwareVersion": self.checkers_info['rsfc']['version']
            },
            "process": self.process,
            "status": { "@id": "schema:CompletedActionStatus" },
            "output": self.output,
            "evidence": self.evidence
        }