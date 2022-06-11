from schemas import Feedback, CreateAndUpdateFeedback


def convertInTime(millis):
    seconds, milliseconds = divmod(millis, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "{0} hours {1} minutes {2} seconds".format(round(hours), round(minutes), round(seconds))


def computePercentage(current, total):
    return current * 100 / total


def getSearchResultStatisticsPerMethod(data, method, provider, resultObj, own=True):
    emptyEntries = 0
    totalEntries = 0
    noOfResults = 0

    for feedback in data:
        if own:
            links = feedback.ownLinks['links']
        else:
            links = feedback.githubLinks[provider]['links']

        if len(links) == 0:
            emptyEntries += 1
        else:
            noOfResults += len(links)

        totalEntries += 1

    res = round(computePercentage(emptyEntries, totalEntries))
    resultObj[method][provider]['emptyEntries'] = str(res) + '%'
    resultObj[method][provider]['nonEmptyEntries'] = str(100 - res) + '%'
    resultObj[method][provider]['avgNumberOfResults'] = round(noOfResults / totalEntries, 1)


def getSearchResultsStatistics(data):
    resultStatistics = {}
    resultStatistics['searchWithTags'] = {'github': {}, 'google': {}}
    resultStatistics['searchWithoutTags'] = {'github': {}}

    # keys: githubLinks -> github, google -> links
    # keys: ownLinks -> links
    getSearchResultStatisticsPerMethod(data, 'searchWithTags', 'github', resultStatistics)
    getSearchResultStatisticsPerMethod(data, 'searchWithTags', 'google', resultStatistics, own=False)
    getSearchResultStatisticsPerMethod(data, 'searchWithoutTags', 'github', resultStatistics, own=False)

    return resultStatistics


def buildStatistics(data):
    userData = {}
    userStatistics = {}
    scenarioStatistics = {}

    for feedback in data:
        key = feedback.extraInfo['userId']

        if key not in userData:
            userData[key] = []

        userData[key].append(feedback)

    for key in userData:
        userData[key].sort(key=lambda x: x.extraInfo['scenarioId'])
        userStatistics[key] = {}
        for i in range(0, len(userData[key])):
            userStatistics[key][userData[key][i].extraInfo['scenarioId']] = {}

    totalAvg = 0
    for key in userData:
        avg = 0
        for i in range(0, len(userData[key])):
            time = 0
            id = userData[key][i].extraInfo['scenarioId']

            if i == 0:
                time = userData[key][0].extraInfo['endTime'] - userData[key][0].extraInfo['startTimeTask']
                userStatistics[key][id]['time'] = convertInTime(time)
                avg += time
            else:
                time = userData[key][i].extraInfo['endTime'] - userData[key][i - 1].extraInfo['endTime']
                userStatistics[key][id]['time'] = convertInTime(time)
                avg += time

            if id not in scenarioStatistics:
                scenarioStatistics[id] = {'averageTime': 0, 'noOfAnswers': 0}

            scenarioStatistics[id]['averageTime'] = scenarioStatistics[id]['averageTime'] + time
            scenarioStatistics[id]['noOfAnswers'] = scenarioStatistics[id]['noOfAnswers'] + 1

        userStatistics[key]['averageUserTime'] = convertInTime(avg / len(userData[key]))
        totalAvg += avg

    userStatistics['totalAverageTimeSpentOnEvaluation'] = convertInTime(totalAvg / len(userData.keys()))

    for key in scenarioStatistics:
        scenarioStatistics[key]['averageTime'] = convertInTime(
            scenarioStatistics[key]['averageTime'] / scenarioStatistics[key]['noOfAnswers'])

    return {'userStatistics': userStatistics, 'scenarioStatistics': scenarioStatistics,
            'searchResultStatistics': getSearchResultsStatistics(data)}
