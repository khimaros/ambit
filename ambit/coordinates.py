# TODO: replace these with cartesian rotation as defined here:
# https://en.wikipedia.org/wiki/Cartesian_coordinate_system#Cartesian_formulae_for_the_plane


def calculate_male_slot(slot, orientation):
    x, y = slot
    if orientation == 0:
        return (x, y + 1)
    if orientation == 90:
        return (x + 1, y)
    if orientation == 180:
        return (x, y - 1)
    if orientation == 270:
        return (x - 1, y)


def calculate_female_slots(slot, orientation):
    x, y = slot
    if orientation == 0:
        return (x + 1, y), (x, y - 1), (x - 1, y)
    if orientation == 180:
        return (x - 1, y), (x, y + 1), (x + 1, y)
    if orientation == 90:
        return (x, y - 1), (x - 1, y), (x, y + 1)
    if orientation == 270:
        return (x, y + 1), (x + 1, y), (x, y - 1)


def calculate_female_slots_wide(slot, orientation):
    x, y = slot
    if orientation == 0:
        return (x + 1, y + 1), (x + 2, y), (x + 1, y - 1), (x, y - 1), (x - 1, y)
    if orientation == 180:
        return (x - 1, y - 1), (x - 2, y), (x - 1, x + 1), (x, y + 1), (x + 1, y)
    if orientation == 90:
        return (x + 1, y - 1), (x, y - 2), (x - 1, y - 1), (x - 1, y), (x, y + 1)
    if orientation == 270:
        return (x - 1, y + 1), (x, y + 2), (x + 1, y + 1), (x + 1, y), (x, y - 1)
