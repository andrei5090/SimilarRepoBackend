from schemas import Feedback, CreateAndUpdateFeedback


def convertMillis(millis):
    seconds = (millis / 1000) % 60
    minutes = (millis / (1000 * 60)) % 60
    hours = (millis / (1000 * 60 * 60)) % 24
    return "{0} hours {1} minutes {2} seconds".format(hours, minutes, seconds)


def buildStatistics(data):
    userData = {}
    res = {}

    for feedback in data:
        key = feedback.extraInfo['userId']

        if key not in userData:
            userData[key] = []

        userData[key].append(feedback)

    for key in userData:
        userData[key].sort(key=lambda x: x.extraInfo['scenarioId'])

    for key in userData:
        res[key] = [convertMillis(x['endTime'] - x['startTime']) for x in userData[key]['extraInfo']]

    print("ressss ")
    print(res)

    return res
