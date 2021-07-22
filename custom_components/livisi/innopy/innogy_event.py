class InnogyEvent:
    def __init__(self, evt):

        if "sequenceNumber" in evt:
            self.sequenceNumber = evt["sequenceNumber"]
        if "type" in evt:
            self.type = evt["type"]
        if "namespace" in evt:
            self.sequenceNumber = evt["namespace"]
        if "timestamp" in evt:
            self.timestamp = evt["timestamp"]
        if "source" in evt:
            self.source = evt["source"]

        prop_dict = {}
        for prop in evt["properties"]:

            if "lastchanged" in prop:

                v = evt["properties"][prop]

                prop_dict.update(
                    {
                        prop: {
                            "value": v,
                            "lastchanged": v,
                        }
                    }
                )
            else:
                v = evt["properties"][prop]
                prop_dict.update({prop: {"value": v}})

        self.properties_dict = prop_dict

        if "link" in evt:
            self.link_dict = evt["link"]
