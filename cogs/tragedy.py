import discord
from discord.ext import commands

class tragedy(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command()
    async def tragedy(self, ctx):
        await ctx.send("Did you :point_right: ever :calendar: hear :ear: the tragedy :scream::sweat::sob: of Darth :imp::levitate: Plagueis :relieved: The Wise :raised_hands:?\n\n\
I :eye: thought :thought_balloon::thinking: not. It’s not a story :book: the Jedi :triumph: would tell :speaking_head::mega: you :point_left:. \
It’s a Sith :smiling_imp: legend :fearful::anguished:. Darth :skull: Plagueis :relieved: was a Dark :new_moon: Lord :crown: of the Sith :smiling_imp:, \
so powerful :muscle: and so wise :raised_hands: he :busts_in_silhouette: could use :call_me_tone1: the Force :hand_splayed: to influence :upside_down: \
the midichlorians :eyes: to create :100::slight_smile:... life :heartbeat:. He :man: had such a knowledge :mortar_board: of the dark :new_moon_with_face: \
side :point_left::point_right: that he :man: could even :night_with_stars: keep :ok_hand: the ones :triumph: he :man: cared :heart_eyes: about :thinking::thought_balloon: from dying :skull:.\n\n\
The dark :new_moon: side :person_wearing_turban: of the Force :hand_splayed: is a pathway :evergreen_tree: to many :two_men_holding_hands: abilities :muscle: some consider :thinking: to be unnatural :alien:. \
He :busts_in_silhouette: became :question: so powerful… the only thing :clock2: he :man: was afraid :scream: of was losing :sob::third_place: his :sweat_drops: power :battery:, which eventually :knife::dagger:, \
of course :race_car:, he :busts_in_silhouette: did. Unfortunately :hushed:, he :busts_in_silhouette: taught :book: his :sweat_drops: apprentice :man: everything :100: he :man: knew :thinking:, then his :sweat_drops: \
apprentice :man: killed :skull_crossbones: him :older_man: in his :wave: sleep :zzz:. Ironic :joy:. He :busts_in_silhouette: could save :floppy_disk::sos: others :couple::two_women_holding_hands::two_men_holding_hands: \
from death :skull:, but :peach::joy::envelope_with_arrow: not himself :triumph:.")
        
def setup(client):
    client.add_cog(tragedy(client))