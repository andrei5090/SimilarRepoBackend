from schemas import Feedback, CreateAndUpdateFeedback
from .metrics import apk
from .google import google_search


def convertInTime(millis):
    seconds, milliseconds = divmod(millis, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "{0} hours {1} minutes {2} seconds".format(round(hours), round(minutes), round(seconds))


def computePercentage(current, total):
    return current * 100 / total


def createScenarioLinkMapping(links):
    mapping = {}
    id = 0
    for link in links:
        mapping[link] = id
        id += 1
    return mapping


def getAPK(links, preferences, k=3):
    mapping = createScenarioLinkMapping(links)
    a = apk([mapping[x] for x in links], [mapping[x] for x in preferences], k)
    return a


# TODO: Add hits
def getSearchResultStatisticsPerMethod(data, method, provider, resultObj, own=True):
    emptyEntries = 0
    totalEntries = 0
    noOfResults = 0

    for feedback in data:
        if own:
            links = feedback.ownLinks['links']
        else:
            if provider == 'google' and 'valid' in feedback.githubLinks[provider] and not \
                    feedback.githubLinks[provider]['valid']:
                continue
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
    # TODO: How many bachelor students
    # TODO: How many male how many female
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
    githubWithTags = 0
    githubWithoutTags = 0
    googleWithTags = 0

    for key in userData:
        avg = 0
        githubWithoutTagsAPK = 0
        googleAPK = 0
        githubWithTagsAPK = 0
        googleInvalidCount = 0
        for i in range(0, len(userData[key])):
            time = 0
            id = userData[key][i].extraInfo['scenarioId']

            # compute APK for each technique
            userStatistics[key][id]['APKGithubWithoutTags'] = getAPK(
                userData[key][i].githubLinks['github']['links'],
                userData[key][i].githubPreferences['github']['checked']) if len(
                userData[key][i].githubLinks['github']['links']) > 0 else 0

            userStatistics[key][id]['APKGoogle'] = getAPK(
                userData[key][i].githubLinks['google']['links'],
                userData[key][i].githubPreferences['google']['checked']) if len(
                userData[key][i].githubLinks['google']['links']) > 0 else 0

            if 'valid' in userData[key][i].githubLinks['google'] and not userData[key][i].githubLinks['google'][
                'valid']:
                googleInvalidCount += 1

            userStatistics[key][id]['APKGithubWithTags'] = getAPK(
                userData[key][i].ownLinks['links'],
                userData[key][i].ownPreferences['checked']) if len(
                userData[key][i].ownLinks['links']) > 0 else 0

            githubWithoutTagsAPK += userStatistics[key][id]['APKGithubWithoutTags']
            githubWithTagsAPK += userStatistics[key][id]['APKGithubWithTags']
            googleAPK += userStatistics[key][id]['APKGoogle']

            if i == 0:
                time = userData[key][0].extraInfo['endTime'] - userData[key][0].extraInfo['startTimeTask']
                userStatistics[key][id]['time'] = convertInTime(time)
                avg += time
            else:
                time = userData[key][i].extraInfo['endTime'] - userData[key][i - 1].extraInfo['endTime']
                userStatistics[key][id]['time'] = convertInTime(time)
                avg += time

            if id not in scenarioStatistics:
                scenarioStatistics[id] = {'averageTime': 0, 'noOfAnswers': 0, 'noOfAnswersGoogleValid': 0}

            scenarioStatistics[id]['averageTime'] = scenarioStatistics[id]['averageTime'] + time
            scenarioStatistics[id]['noOfAnswers'] = scenarioStatistics[id]['noOfAnswers'] + 1
            if not ('valid' in userData[key][i].githubLinks['google'] and not userData[key][i].githubLinks['google'][
                'valid']):
                scenarioStatistics[id]['noOfAnswersGoogleValid'] += 1

        userStatistics[key]['averageUserTime'] = convertInTime(avg / len(userData[key]))

        userStatistics[key]['githubWithTagsAPKAverage'] = githubWithTagsAPK / len(userData[key])
        userStatistics[key]['githubWithoutTagsAPKAverage'] = githubWithoutTagsAPK / len(userData[key])
        userStatistics[key]['googleAPKAverage'] = googleAPK / (len(userData[key]) - googleInvalidCount) if (len(
            userData[key]) - googleInvalidCount) > 0 else 1

        githubWithTags += userStatistics[key]['githubWithTagsAPKAverage']

        githubWithoutTags += userStatistics[key]['githubWithoutTagsAPKAverage']

        googleWithTags += userStatistics[key]['googleAPKAverage']

        totalAvg += avg

    userStatistics['totalAverageTimeSpentOnEvaluation'] = convertInTime(totalAvg / len(userData.keys()))

    searchStatistics = getSearchResultsStatistics(data)

    for key in scenarioStatistics:
        scenarioStatistics[key]['averageTime'] = convertInTime(
            scenarioStatistics[key]['averageTime'] / scenarioStatistics[key]['noOfAnswers'])

        searchStatistics['searchWithTags']['github']['MAPK'] = githubWithTags / scenarioStatistics[key]['noOfAnswers']
        searchStatistics['searchWithTags']['google']['MAPK'] = googleWithTags / scenarioStatistics[key][
            'noOfAnswersGoogleValid']
        searchStatistics['searchWithoutTags']['github']['MAPK'] = githubWithoutTags / scenarioStatistics[key][
            'noOfAnswers']

    return {'userStatistics': userStatistics, 'scenarioStatistics': scenarioStatistics,
            'searchResultStatistics': searchStatistics}


def getNotValidGoogleSearches(data):
    totalCount = 0
    invalidGoogleResultsId = []
    for feedback in data:
        query = ''
        query += feedback.extraInfo['queryData']['queryText']
        for i in feedback.extraInfo['queryData']['tags']:
            query += ' ' + i

        if len(feedback.githubLinks['google']['links']) == 0 and len(google_search(query)['links']) > 0:
            totalCount += 1
            invalidGoogleResultsId.append(feedback.id)

    return invalidGoogleResultsId
