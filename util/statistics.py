from schemas import Feedback, CreateAndUpdateFeedback


def convertMillis(millis):
    seconds = (millis / 1000) % 60
    minutes = (millis / (1000 * 60)) % 60
    hours = (millis / (1000 * 60 * 60)) % 24
    return "{0} hours {1} minutes {2} seconds".format(round(hours), round(minutes), round(seconds))


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
        res[key] = {}
        for i in range(0, len(userData[key])):
            res[key][userData[key][i].extraInfo['scenarioId']] = {}

    totalAvg = 0
    for key in userData:
        avg = 0
        for i in range(0, len(userData[key])):
            if i == 0:
                time = userData[key][0].extraInfo['endTime'] - userData[key][0].extraInfo['startTimeTask']
                res[key][userData[key][i].extraInfo['scenarioId']]['time'] = convertMillis(time)
                avg += time
            else:
                time = userData[key][i].extraInfo['endTime'] - userData[key][i - 1].extraInfo['endTime']
                res[key][userData[key][i].extraInfo['scenarioId']]['time'] = convertMillis(time)
                avg += time

        res[key]['averageTimeSpentPerTask'] = convertMillis(avg / len(userData[key]))
        totalAvg += avg

    res['totalAverageTimeSpent'] = convertMillis(totalAvg / len(userData.keys()))

    return res
