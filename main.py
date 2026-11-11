
from drafter import *
from dataclasses import dataclass
from bakery import assert_equal
#Library used to convert a string into a file object
import io
#Dataclasses
@dataclass
class Hotspot:
    """
    A dataclass that represents a place where someone has birdwatched.
    Attributes:
        name(str): The name of the hotspot location.
        total(int): The total number of bird seen at this location.
        birds_local(list[str]): A list of Bird species names, that
            represents the birds seen at this location.
        location(str): A string representing the state and county of the hotspot.
    """
    name: str
    total: int
    birds_local: list[str]
    location: str
    
@dataclass
class Bird:
    """
    species(str): The name of the bird species.
    count(int): The total number of this species you have seen.
    hotspots_bird(list[str]): A list of Hotspot names, that
        represent the locations you have seen this bird at. 
    """
    species: str
    count: int
    hotspots_bird: list[str]
    
@dataclass
class Sighting:
    #species and name are the names for a bird species and hotspot, respectively
    """
    The simplest dataclass that contains relevant data from a formatted .csv file
        to be proccessed further.
    Attributes:
    species(str): The name of a bird species sighted
    count(str): The number of the bird sighted as a string.
    state(str): The state or providence the bird was sighted in.
    county(str): The county the bird was sighted in.
    name(str): The name of the place (to be Hotspot) the bird was
        sighted in.  
    """
        
    species: str
    count: str
    state: str
    county: str
    name: str

@dataclass
class State:
    """
    The current state of the Birding Data Application.
    Attributes:
        file_raw(str): The file as a raw string as imported by FileUpload.
        file(file object): The actual file object after applying StringIO to file_raw.
        sightings(list[Sighting]): A list of Sighting dataclasses, representing a
            single observation of a number of birds at a given place.
        birds(list[Bird]) A list of Bird dataclasses, which represents a species,
            how many of then you have seen, and the places you have seen the bird
            at.
        hotspots(list[Hotspot]): A list of Hotspot dataclasses, which represents a
            place that you go to birdwatch, including its name, a list of bird seen there,
            and the total number of birds seen there.
        summary(int): An integer representing what page of the data summary should be loaded.
    """
    file_raw: str
    file: str
    sightings: list[Sighting]
    birds: list[Bird]
    hotspots: list[Hotspot]
    summary: int



#Route Functions (UNIT TESTS AT BOTTOM OF CODE)
@route
def index(state: State) -> Page:
    """
    The index function that takes in a state dataclass and produces a
        web page with the correct content.
    Args:
        state (State): An instance of the state dataclass.
    Returns:
        Page: a web page with the correct content. 
    """
    return Page(state, [Header('Upload your data!'),
            '''Steps:\n1. Export your eBird Data from "https://ebird.org/myebird"
            2. Unzip the file!
            3. Select your file from the menu.
            There are several sample files available in the GitHub documentation.\n''',
            FileUpload("file_raw", accept = ".csv"), Button("Continue!",'get_data')])

@route
def get_data(state: State, file_raw: str) -> Page:
    """
    Converts the unproccessed formatted .csv file into a state dataclass, and returns
        a page that allows the user to navigate the website.
    Args:
        state (State): An instance of the state dataclass.
        file_raw(str): The name of the users ebird .csv data file.
    Returns:
        Page: a web page with the correct content.     
    """
    state.file_raw = file_raw
    #converts the string version of the file as imported by FileUpload() into a file object
    state.file = io.StringIO(file_raw)
    state.sightings = data_to_sightings(state.file)
    state.birds = sightings_to_birds(state.sightings)
    state.hotspots = sightings_to_hotspots(state.sightings)
    state.summary = 0
    return Page(state, [Header("My Ebird Data Home"), Button('New Data File', 'reset_data'),
            Button('View My Birds', 'bird_hub'), Button('View My Hotspots', 'hotspot_hub'),
            Button('My Birding Summary', 'birding_stats')])

@route
def reset_data(state: State) -> Page:
    """
    Resets the state of the web page do allow the user to enter a different file.
    Args:
        state(State): The current state of the Birding Data Application.
    Returns:
        Page: A page that allows the user to enter a different file name.
    """
    state.file_raw = ''
    state.file = ''
    state.sightings = []
    state.birds = []
    state.hotspots = []
    state.summary = 0
    return index(state)

@route
def bird_hub(state: State) -> Page:
    """
    Creates a page with a list buttons representing all species in the file.
        The buttons link to bird pages.
    Args:
        state(State): The current state of the Birding Data Application.
    Returns:
        Page: A page with a list of buttons for each bird in the file.
    """
    buttons = []
    for bird in state.birds:
        buttons.append(Button(bird.species, 'bird', [Argument('species', bird.species)]))
    
    return Page(state,[Header('Your Birds:'), Text("You have seen " + str(len(state.birds)) +
                    " species!"), '\nSearch For a Bird:\n', TextBox('species'),
                    Button('Search', 'bird'), BulletedList(buttons), '\n',
                    Button('Home', 'get_data', [Argument("file_raw", state.file_raw)])])

@route
def hotspot_hub(state: State) -> Page:
    """
    Creates a page with a list buttons representing all hotspots in the file.
        The buttons link to bird pages.
    Args:
        state(State): The current state of the Birding Data Application.
    Returns:
        Page: A page with a list of buttons for each hotspot in the file.
    """
    buttons = []
    for hotspot in state.hotspots:
        buttons.append(Button(hotspot.name, 'hotspot', [Argument('name', hotspot.name)]))
    return Page(state, [Header('Your Hotspots:'), Text("You have been to " + str(len(state.hotspots)) +
                         " hotspots!"), '\nSearch For a Hotspot:\n', TextBox('name'),
                         Button('Search', 'hotspot'),BulletedList(buttons), '\n',
                        Button('Home', 'get_data', [Argument("file_raw", state.file_raw)]) ])

@route
def birding_stats(state: State) -> Page:
    #Function could be decomposed, but I believe it is most legible like this-shows how state.summary is being used.
    """
    Loads several pages that summarize your biggest birding statistics,
        including: total species seen, total birds seen, most seen bird,
        most birds seen at a hotspot, and most species seen at a hotspot.
        Works by adding + 1 to the state.summary_page attribute to tell
        the program which page to load. 
    Args:
        state(State): The current state of the Birding Data Application.
    Returns:
        Page: A page with one of your big bird stats and a picture of a bird. 
    """
    #Page that tells the user the total number of species seen in the given data.
    if state.summary == 0:
        state.summary += 1
        return Page(state,[Header("Total Species:"), Image("1.jpg",500,500), '\n',
                           Text("You have seen " + str(len(state.birds)) +
                                                   " species!"),'\n',
                           Button("Next Stat", 'birding_stats')])
    #Page that tells the user the total number of birds they have seen in the given data.
    if state.summary == 1:
        state.summary += 1
        total_birds = 0
        for bird in state.birds:
            total_birds += bird.count
        return Page(state,[Header("Total Birds:"), Image("2.jpg",500,500), '\n',
                           Text("You have seen " + str(total_birds) +
                                                   " birds!"),"\n",
                           Button("Next Stat", 'birding_stats')])
    #Page that tells the user the bird that they have seen the most of in the given data.
    if state.summary == 2:
        state.summary += 1
        most_seen = Bird("Bird of Washington", 0, [])
        for bird in state.birds:
            if bird.count > most_seen.count:
                most_seen = bird
        return Page(state,[Header("Most Seen Bird:"), Image("3.jpg",500,500), '\n',
                           Text("You have seen " + str(most_seen.count) +
                            " " + most_seen.species + "! " "\nThis is your most seen bird!"),
                           "\n", Button("Next Stat", 'birding_stats')])
    #Page that tells the user the hotspot that they have seen the most birds in, in the given data.
    if state.summary == 3:
        state.summary += 1
        most_birds = Hotspot('Nowhere', 0, [], 'Nowhere')
        for hotspot in state.hotspots:
            if hotspot.total > most_birds.total:
                most_birds = hotspot
        return Page(state,[Header("Most Birds at a Hotspot:"), Image("4.jpg",500,500), '\n',
                           Text("You have seen " + str(most_birds.total) +
                            " birds at " + most_birds.name + " in " +
                                most_birds.location  +
                                "!\nThis is the most birds you have seen in one spot!"),
                           "\n", Button("Next Stat", 'birding_stats')])
    #Page that tells the user the hotspot they have seen the most bird species in, in the given data.
    #Links to home page (get_data route).
    if state.summary == 4:
        state.summary += 1
        most_species = Hotspot('Nowhere', 0, [], 'Nowhere')
        for hotspot in state.hotspots:
            if len(hotspot.birds_local) > len(most_species.birds_local):
                most_species = hotspot
        return Page(state,[Header("Most Species at a Hotspot:"), Image("5.jpg", 500,500), '\n',
                           Text("You have seen " + str(len(most_species.birds_local)) +
                            " species at " + most_species.name + " in " + most_species.location  +
                                "!\nThis is the most species you have seen in one spot!"),
                           "\n", Button('Home', 'get_data', [Argument("file_raw", state.file_raw)]) ])

@route
def bird(state: State, species: str) -> Page:
    """
    Creates a page with information about your sightings of one bird.
    Args:
        state(State): The current state of the Birding Data Application.
        species(str): The name of the bird species.
    Returns:
        Page: Content about sightings of a specific bird species.
    """
    a_bird = None
    for bird in state.birds:
        if species.upper() == bird.species.upper():
            a_bird = bird
    if not a_bird:
        return Page(state, [Header("Oops! Bird not found!"), "You haven't seen any " + species
                            + " yet! \nMake sure you spelled your bird correctly!\n",
                            Button('More Birds!', 'bird_hub'), '\n', Button('Home', 'get_data',
                                                    [Argument("file_raw", state.file_raw)])])
    
    hotspot_buttons = []
    for name in a_bird.hotspots_bird:
        for hotspot in state.hotspots:
            if name == hotspot.name:
                hotspot_buttons.append(Button(name, 'hotspot', [Argument('name', hotspot.name)]))
    return Page(state,[Header(a_bird.species), 'You have seen ' +str(a_bird.count) + " " +
                       a_bird.species + "!", ' \nYou have seen ' + a_bird.species +' at these hotspots:',
                       BulletedList(hotspot_buttons), '\n', Button('More Birds!', 'bird_hub'), '\n',
                       Button('Home', 'get_data', [Argument("file_raw", state.file_raw)])])

@route
def hotspot(state: State, name: str) -> Page:
    """
    Creates a page with information about your stats in one hotspot.
    Args:
        state(State): The current state of the Birding Data Application.
        name(str): The name of the hotspot location.
    Returns:
        Page: Content about stats for a specific hotspot.
    """
    a_hotspot = None
    for hotspot in state.hotspots:
        if name.upper() == hotspot.name.upper():
            a_hotspot = hotspot
    if not a_hotspot:
        return Page(state, [Header("Oops! Hotspot not found!"),
                            "You haven't been anywhere called " + name +
                            " yet! \nMake sure you spelled your Hotspot name correctly!\n",
                            Button('More Hotspots!', 'hotspot_hub'), '\n', Button('Home', 'get_data',
                                                        [Argument("file_raw", state.file_raw)])])
    
    bird_buttons = []
    for species in a_hotspot.birds_local:
        for bird in state.birds:
            if species == bird.species:
                bird_buttons.append(Button(species, 'bird', [Argument('species', bird.species)]))
    return Page(state,[Header(a_hotspot.name), "Location: " + a_hotspot.location,'\nYou have seen '
                       + str(a_hotspot.total) + " birds at this hotspot! \nYou have seen",
                       str(len(a_hotspot.birds_local)),
                       ' species at this hotspot!\nYou have seen these birds here:',
                       BulletedList(bird_buttons),'\n', Button('More Hotspots!', 'hotspot_hub'), '\n',
                       Button('Home', 'get_data', [Argument("file_raw", state.file_raw)]) ])

#Helper Functions:
def data_to_sightings(file: str) -> list[Sighting]:
    """
    Helper to get_data route, gets the unproccessed formatted .csv file
        and creates a list of Sighting Dataclasses.
    Args:
        file_raw(str): The name of the users ebird .csv data file.
    Returns:
        list[Sighting]: A list of sighting dataclasses, representing all observations from
            the users file.
    """
#    data = open(file)
    sightings = []
    for line in file:
        sighting = line.split(',')
        if sighting[4] == 'X':
            sighting[4] = '1'
        sightings.append(Sighting(sighting[1],sighting[4],
                                  sighting[5][3:], sighting[6],
                                  sighting[8]))
#    data.close()
    return sightings[1:]

#Testing Mini Dataset Constants
Data1 = open("TestData1.csv")
Data2 = open("TestData2.csv")
Data3 = open("TestData3.csv")

Test1 = data_to_sightings(Data1)
Test2 = data_to_sightings(Data2)
Test3 = data_to_sightings(Data3)

assert_equal(Test1, [
    Sighting(species='Golden-crowned Kinglet', count='1', state='DE',
             county='Sussex', name='Cape Henlopen SP-- Fishing Pier'),
    Sighting(species='White-breasted Nuthatch', count='7', state='DE',
             county='New Castle', name='Ashland Nature Center and Hawk Watch'),
    Sighting(species='White-breasted Nuthatch', count='1', state='DE',
             county='New Castle', name='Bellevue State Park'),
    Sighting(species='Double-crested Cormorant', count='1', state='DE',
             county='New Castle', name='Bellevue State Park'),
    Sighting(species='American Goldfinch', count='2', state='DE',
             county='New Castle', name='Bellevue State Park')] )

assert_equal(Test2, [
    Sighting(species='Laughing Gull', count='42', state='DE',
             county='Sussex', name='Cape Henlopen SP-- Fishing Pier'),
    Sighting(species='Laughing Gull', count='2', state='DE',
             county='Sussex', name='Cape Henlopen SP-- Fishing Pier'),
    Sighting(species='White-breasted Nuthatch', count='1', state='DE',
             county='New Castle', name='Bellevue State Park'),
    Sighting(species='Chimney Swift', count='2', state='DE',
             county='New Castle', name='Battery Park'),
    Sighting(species='tern sp.', count='50', state='DE',
             county='Kent', name='Bombay Hook NWR--Shearness Pool')])

assert_equal(Test3, [
    Sighting(species='Double-crested Cormorant', count='1', state='DE',
             county='Sussex', name='Cape Henlopen SP--Fort Miles'),
    Sighting(species='Double-crested Cormorant', count='1', state='DE',
             county='Sussex', name="Cape Henlopen SP--Gordon's Pond"),
    Sighting(species='Double-crested Cormorant', count='80', state='DE',
             county='Sussex', name="Cape Henlopen SP--Gordon's Pond Trail north"),
    Sighting(species='Double-crested Cormorant', count='5', state='DE',
             county='Sussex', name='Cape Henlopen SP--The Point'),
    Sighting(species='Double-crested Cormorant', count='28', state='DE',
             county='Sussex', name='Cape Henlopen SP--The Point')])

def get_hotspot_names(sightings: list[Sighting]) -> list[str]:
    """
    Helper to sightings_to_hotspots, filters sighting list for unique hotspot names.
        Creates a list of those names.
    Args:
        sightings(list[Sighting]):list[Sighting]: A list of sighting dataclasses,
            representing all observations from the users file.
    Returns:
        list[str]: Representing the names of all hotspots the user has birded at.
    """
    hotspot_names = []
    for sighting in sightings:
        if sighting.name not in hotspot_names:
            hotspot_names.append(sighting.name)
    return hotspot_names

assert_equal(get_hotspot_names(Test1), ['Cape Henlopen SP-- Fishing Pier',
                                        'Ashland Nature Center and Hawk Watch',
                                        'Bellevue State Park'])
assert_equal(get_hotspot_names(Test2), ['Cape Henlopen SP-- Fishing Pier',
                                        'Bellevue State Park',
                                        'Battery Park',
                                        'Bombay Hook NWR--Shearness Pool'])
assert_equal(get_hotspot_names(Test3), ['Cape Henlopen SP--Fort Miles',
                                        "Cape Henlopen SP--Gordon's Pond",
                                        "Cape Henlopen SP--Gordon's Pond Trail north",
                                        'Cape Henlopen SP--The Point'])

def get_hotspot_total(name: str, sightings: list[Sighting]) -> int:
    """
    Helper to sightings_to_hotspots, gets the total number of birds seen at a
        single hotspot.
    Args:
        name(str): The name of the hotspot location.
        sightings(list[Sighting]):list[Sighting]: A list of sighting dataclasses,
            representing all observations from the users file.
    Returns:
        int: The number of birds seen at that hotspot.
    """
    total = 0
    for sighting in sightings:
        if name == sighting.name:
            total += int(sighting.count)
    return total

assert_equal(get_hotspot_total('Bellevue State Park', Test1), 4)
assert_equal(get_hotspot_total('Cape Henlopen SP-- Fishing Pier', Test2), 44)
assert_equal(get_hotspot_total('Cape Henlopen SP--The Point', Test3), 33)

def get_hotspot_location(name: str, sightings: list[Sighting]) -> str:
    """
    Helper to sightings_to_hotspots, gets the location of the hotspot in terms
        of county and state.
    Args:
        name(str): The name of the hotspot location.
        sightings(list[Sighting]):list[Sighting]: A list of sighting dataclasses,
            representing all observations from the users file.
    Returns:
        str: A string represnting the location of a hotspot. 
    """
    for sighting in sightings:
        if sighting.name == name:
            return sighting.county + ', ' + sighting.state
    return "Unknown"


def get_bird_species(sightings: list[Sighting]) -> list[str]:
    """
    Helper to sightings_to_birds, filters sighting list for unique bird species.
        Creates a list of those species.
    Args:
        sightings(list[Sighting]):list[Sighting]: A list of sighting dataclasses,
            representing all observations from the users file.
    Returns:
        list[str]: Representing the species of all the birds the user has seen.
    """
    bird_species = []
    for sighting in sightings:
        if sighting.species not in bird_species:
            bird_species.append(sighting.species)
    return bird_species
assert_equal(get_bird_species(Test1), ['Golden-crowned Kinglet', 'White-breasted Nuthatch',
                                       'Double-crested Cormorant','American Goldfinch'])
assert_equal(get_bird_species(Test2), ['Laughing Gull', 'White-breasted Nuthatch',
                                       'Chimney Swift', 'tern sp.'])
assert_equal(get_bird_species(Test3), ['Double-crested Cormorant'])


def get_count(species: str, sightings: list[Sighting]) -> int:
    """
    Helper to sightings_to_birds, gets the total count of a species seen.
    Args:
        species(str): The name of the bird species.
        sightings(list[Sighting]):list[Sighting]: A list of sighting dataclasses,
            representing all observations from the users file.
    Returns:
        int: The total number of this species you have seen.
    
    """
    count = 0
    for sighting in sightings:
        if species == sighting.species:
            count += int(sighting.count)
    return count

assert_equal(get_count('Double-crested Cormorant', Test3), 115)
assert_equal(get_count('Double-crested Cormorant', Test2), 0)
assert_equal(get_count('NOT A BIRD', Test1), 0)

def get_hotspot_birds(name: str, sightings: list[Sighting]) -> list[str]:
    """
    Helper to sightings_to_hotspots, gets a list of birds seen at a given hotspot name.
    Args:
        name(str): The name of the hotspot location.
        sightings(list[Sighting]):list[Sighting]: A list of sighting dataclasses,
            representing all observations from the users file.
    Returns:
        list[str] A list of Bird species names, that represents the birds seen at this location. 
    """
    birds_local = []
    for sighting in sightings:
        if name == sighting.name and sighting.species not in birds_local:
            birds_local.append(sighting.species)
    return birds_local

assert_equal(get_hotspot_birds('Bellevue State Park', Test1), ['White-breasted Nuthatch',
                                                               'Double-crested Cormorant',
                                                               'American Goldfinch'])
assert_equal(get_hotspot_birds('Cape Henlopen SP-- Fishing Pier', Test2), ['Laughing Gull'])
assert_equal(get_hotspot_birds('Ashland Nature Center and Hawk Watch', Test3), [])

                
            
def get_bird_hotspots(species: str, sightings: list[Sighting]) -> list[str]:
    """
    Helper to sightings_to_birds, gets a list of hotspots this bird was seen at.
    Args:
        species(str): The name of the bird species.
        sightings(list[Sighting]):list[Sighting]: A list of sighting dataclasses,
            representing all observations from the users file.
    Returns:
        list[str]: A list of Hotspot names, that represent the locations
            you have seen this bird at. 
    """
    hotspots_bird = []
    for sighting in sightings:
        if species == sighting.species and sighting.name not in hotspots_bird:
            hotspots_bird.append(sighting.name)
    return hotspots_bird

assert_equal(get_bird_hotspots('White-breasted Nuthatch', Test1),
             ['Ashland Nature Center and Hawk Watch', 'Bellevue State Park'])
assert_equal(get_bird_hotspots('American Goldfinch', Test2), [])
assert_equal(get_bird_hotspots('Double-crested Cormorant', Test3),
                               ['Cape Henlopen SP--Fort Miles',
                               "Cape Henlopen SP--Gordon's Pond",
                               "Cape Henlopen SP--Gordon's Pond Trail north",
                               'Cape Henlopen SP--The Point'])

def sightings_to_hotspots(sightings: list[Sighting]) -> list[Hotspot]:
    """
    Helper to get_data route, gets the data from list of Sighting Dataclasses and
        creates a list of Hotspot Dataclasses.
    Args:
        sightings(list[Sighting]):list[Sighting]: A list of sighting dataclasses,
            representing all observations from the users file.
    Returns:
        list[Hotspot]: A list of Hotspot dataclasses, representing all the places
            the user has went birding.  
    """
    hotspots =[]
    for name in get_hotspot_names(sightings):
        hotspots.append(Hotspot(name, get_hotspot_total(name, sightings),
                                get_hotspot_birds(name, sightings),
                                get_hotspot_location(name, sightings)))
    return hotspots

assert_equal(sightings_to_hotspots(Test1), [Hotspot(name='Cape Henlopen SP-- Fishing Pier', total=1,
                                                    birds_local=['Golden-crowned Kinglet'],
                                                    location='Sussex, DE'),
                                            Hotspot(name='Ashland Nature Center and Hawk Watch',
                                                    total=7,
                                                    birds_local=['White-breasted Nuthatch'],
                                                    location='New Castle, DE'),
                                            Hotspot(name='Bellevue State Park', total=4,
                                                    birds_local=['White-breasted Nuthatch',
                                                                 'Double-crested Cormorant',
                                                                 'American Goldfinch'],
                                                    location='New Castle, DE')])
assert_equal(sightings_to_hotspots(Test2), [Hotspot(name='Cape Henlopen SP-- Fishing Pier', total=44,
                                                    birds_local=['Laughing Gull'],
                                                    location='Sussex, DE'),
                                            Hotspot(name='Bellevue State Park', total=1,
                                                    birds_local=['White-breasted Nuthatch'],
                                                    location='New Castle, DE'),
                                            Hotspot(name='Battery Park', total=2,
                                                    birds_local=['Chimney Swift'],
                                                    location='New Castle, DE'),
                                            Hotspot(name='Bombay Hook NWR--Shearness Pool',
                                                    total=50, birds_local=['tern sp.'],
                                                    location='Kent, DE')])
assert_equal(sightings_to_hotspots(Test3), [Hotspot(name='Cape Henlopen SP--Fort Miles', total=1,
                                                    birds_local=['Double-crested Cormorant'],
                                                    location='Sussex, DE'),
                                            Hotspot(name="Cape Henlopen SP--Gordon's Pond", total=1,
                                                    birds_local=['Double-crested Cormorant'],
                                                    location='Sussex, DE'),
                                            Hotspot(name="Cape Henlopen SP--Gordon's Pond Trail north",
                                                    total=80,
                                                    birds_local=['Double-crested Cormorant'],
                                                    location='Sussex, DE'),
                                            Hotspot(name='Cape Henlopen SP--The Point', total=33,
                                                    birds_local=['Double-crested Cormorant'],
                                                    location='Sussex, DE')])

def sightings_to_birds(sightings: list[Sighting]) -> list[Bird]:
    """
    Helper to get_data route, gets the data from list of Sighting Dataclasses and
        creates a list of Bird Dataclasses.
    Args:
        sightings(list[Sighting]):list[Sighting]: A list of sighting dataclasses,
            representing all observations from the users file.
    Returns:
        list[Bird] A list of Bird dataclasses, which represents a species,
            how many of then you have seen, and the places you have seen the bird
            at. 
    """
    birds = []
    for species in get_bird_species(sightings):
        birds.append(Bird(species, get_count(species, sightings), get_bird_hotspots(species, sightings)))
    return birds

assert_equal(sightings_to_birds(Test1), [Bird(species='Golden-crowned Kinglet', count=1,
                                              hotspots_bird=['Cape Henlopen SP-- Fishing Pier']),
                                         Bird(species='White-breasted Nuthatch', count=8,
                                              hotspots_bird=['Ashland Nature Center and Hawk Watch',
                                                             'Bellevue State Park']),
                                         Bird(species='Double-crested Cormorant', count=1,
                                              hotspots_bird=['Bellevue State Park']),
                                         Bird(species='American Goldfinch', count=2,
                                              hotspots_bird=['Bellevue State Park'])])
assert_equal(sightings_to_birds(Test2), [Bird(species='Laughing Gull', count=44,
                                              hotspots_bird=['Cape Henlopen SP-- Fishing Pier']),
                                         Bird(species='White-breasted Nuthatch', count=1,
                                              hotspots_bird=['Bellevue State Park']),
                                         Bird(species='Chimney Swift', count=2,
                                              hotspots_bird=['Battery Park']),
                                         Bird(species='tern sp.', count=50,
                                              hotspots_bird=['Bombay Hook NWR--Shearness Pool'])])
assert_equal(sightings_to_birds(Test3), [Bird(species='Double-crested Cormorant', count=115,
                                              hotspots_bird=['Cape Henlopen SP--Fort Miles',
                                                             "Cape Henlopen SP--Gordon's Pond",
                                                             "Cape Henlopen SP--Gordon's Pond Trail north",
                                                             'Cape Henlopen SP--The Point'])])



#Route Unit Tests
assert_equal(index(State('','',[],[],[], 0)), Page(State('','',[],[],[], 0), [Header('Upload your data!'),
            '''Steps:\n1. Export your eBird Data from "https://ebird.org/myebird"
            2. Unzip the file!
            3. Select your file from the menu.
            There are several sample files available in the GitHub documentation.\n''',
            FileUpload("file_raw", accept = ".csv"), Button("Continue!",'get_data')]) )

assert_equal(reset_data(State(Data1.read(),Data1,data_to_sightings(Data1),
                              sightings_to_birds(Test1), sightings_to_hotspots(Test1), 0)),
             index(State('','',[],[],[], 0)))

"""The following route funtions are not required to be tested because they include
file objects, which have a randomized code as an identifier:
get_data
bird_hub
hotspot_hub
bird
hotspot
birding_stats
"""

Data1.close()
Data2.close()
Data3.close()


#Server Start
start_server(index(State("",'',[],[], [], 0)))
