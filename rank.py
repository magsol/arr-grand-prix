import argparse
import os.path
from datetime import datetime, date

import pandas as pd

def _age(birthday, current_year):
    """
    Helper function for computing a person's age, for the purposes
    of the Grand Prix.

    The policy is: THE PERSON'S AGE FOR THE DURATION OF THE COMPETITION
    YEAR IS THE AGE THEY WILL BECOME IN THAT YEAR.
    """
    return current_year - birthday.year

def parse_membership(f):
    """
    Parses out the active membership from the CSV file.

    Parameters
    ----------
    f : string
        Path to a CSV file containing the active ARR membership.

    Returns
    -------
    """
    members = pd.read_csv(f)
    members = members.drop(["Middle Name", "Membership Type", "Category", "Primary Member", "E-mail", "Phone", "Address", "City", "State", "Country", "Zip Code", "Membership End Date"], axis = 1)
    return members

def get_names(members):
    """
    Helper function to generate "harmless" names of the members.
    """
    return set(map(str.lower, (members["First Name"].map(str) + " " + members["Last Name"]).tolist()))

def ranking(results, members, year,
        ages = [14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 200],
        points = [10, 8, 7, 5, 3, 2, 1]):
    """
    Generates the age group rankings.
    """
    ag_ranks = {}
    for i, age in enumerate(ages):
        lo = 0 if i == 0 else ages[i - 1] + 1
        hi = age
        key = "{}-{}".format(lo, hi)
        value = {"F": [], "M": []}
        ag_ranks[key] = value

    # Go through the results.
    for r in results:
        fullname, place = r
        first_name, *last_name = fullname.split(" ")
        last_name = " ".join(last_name)

        # Look up the person in the membership directory.
        people = members[ members["First Name"].str.contains(first_name, case = False) ]
        if people.shape[0] > 1:
            person = people[ people["Last Name"].str.contains(last_name, case = False) ]
            if person.shape[0] > 1:
                exit("Name '{}' is ambiguous in the membership list!".format(fullname))
        else:
            person = people

        # Cool, now get their gender and age.
        gender = person.Gender.item()
        bday = datetime.strptime(person["Date of Birth"].item(), "%m/%d/%Y")
        age = _age(bday, year)

        # Figure out what age group they go in.
        for key in ag_ranks.keys():
            age_lo, age_hi = list(map(int, key.split("-")))
            if age >= age_lo and age <= age_hi:
                # We've found the age group! Append the person's name.
                key = "{}-{}".format(age_lo, age_hi)
                points_index = len(ag_ranks[key][gender])
                award = 0 if points_index >= len(points) else points[points_index]
                ag_ranks[key][gender].append((fullname, award))
    return ag_ranks

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Grand Prix Rankings',
        epilog = 'lol t34mz0rz', add_help = 'How to use',
        prog = 'python rank.py <options>')

    # Required arguments.
    parser.add_argument("-i", "--input", required = True,
        help = "CSV file export of current ARR membership.")
    parser.add_argument("-u", "--url", required = True,
        help = "URL or text file of race results.")

    # Optional arguments.
    parser.add_argument("--year", type = int, default = 2019,
        help = "Current year for age group purposes. [DEFAULT: 2019]")
    parser.add_argument("-o", "--output", default = "output.txt",
        help = "Output file containing the points and rankings. [DEFAULT: output.txt]")

    # Parse out the arguments.
    args = vars(parser.parse_args())
    #if not os.path.isdir(args['output']):
    #    os.mkdir(args['output'])

    # STEP 1: READ IN THE MEMBERSHIP.
    members = parse_membership(args['input'])
    names = get_names(members)

    # STEP 2: READ IN THE RESULTS.
    from classicraceservices import parse_url
    results = parse_url(args['url'], members = names)

    # STEP 3: RANK BY AGE GROUP.
    ranks = ranking(results, members, args['year'])
    f = open(args['output'], "w")
    for key, value in ranks.items():
        for gender in ["M", "F"]:
            f.write("{}{}:\n".format(key, gender))

            winners = ranks[key][gender]
            for (name, points) in winners:
                f.write("\t{} :\t{}\n".format(name, points))
    f.close()
