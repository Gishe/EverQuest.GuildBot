from game.guild.entities.dkp_summary import DkpSummary

from integrations.opendkp.opendkp_gateway import OpenDkpGateway

class OpenDkp:
    def __init__(self):
        self._api_gateway = OpenDkpGateway()

    # Example flow of how we can integrate/push changes to OpenDKP directly
    # TODO: Pass expansion as a parameter
    def create_raid(self, raid_name):
        # TODO: Lookup raid by name and ensure it doesn't exist, or else
        # we will create a duplicate raid with an identical name
        print(self._api_gateway.create_raid(raid_name))

    def get_dkp_summary(self) -> DkpSummary:
        return self._api_gateway.fetch_dkp_summary()
