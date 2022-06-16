from schemas import Feedback, CreateAndUpdateFeedback
from .metrics import apk, precision_at_k, recall_at_k
from .google import google_search
import numpy as np


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


def getAPK(links, preferences, k=5):
    mapping = createScenarioLinkMapping(links)
    a = apk([mapping[x] for x in preferences], [mapping[x] for x in links], k)
    return a


def getPrecisionK(links, preferences, k=5):
    mapping = createScenarioLinkMapping(links)
    y_true = [1 if x in preferences else 0 for x in links]
    y_pred = [1 for x in links]
    a = precision_at_k(y_true, y_pred, k)
    return a


def getRecallK(links, preferences, k=3):
    # mapping = createScenarioLinkMapping(links)
    y_true = [1 if x in preferences else 0 for x in links]
    y_pred = [1 for x in links]
    a = recall_at_k(y_true, y_pred, k)
    return a


# TODO: Add hits
def getSearchResultStatisticsPerMethod(data, method, provider, resultObj, own=True):
    emptyEntries = 0
    totalEntries = 0
    noOfResults = 0
    noOfCheckedResults = 0

    for feedback in data:
        if own:
            links = feedback.ownLinks['links']
            checked_links = feedback.ownPreferences['checked']
        else:
            if provider == 'google' and 'valid' in feedback.githubLinks[provider] and not \
                    feedback.githubLinks[provider]['valid']:
                continue
            links = feedback.githubLinks[provider]['links']
            checked_links = feedback.githubPreferences[provider]['checked']

        if len(links) == 0:
            emptyEntries += 1
        else:
            noOfResults += len(links)

        noOfCheckedResults += len(checked_links)

        totalEntries += 1

    res = round(computePercentage(emptyEntries, totalEntries))
    resultObj[method][provider]['emptyEntries'] = str(res) + '%'
    resultObj[method][provider]['nonEmptyEntries'] = str(100 - res) + '%'
    resultObj[method][provider]['avgNumberOfResults'] = round(noOfResults / totalEntries, 1)
    resultObj[method][provider]['avgNumberOfRelevantItems'] = noOfCheckedResults / totalEntries
    resultObj[method][provider]['proportionOfRelevantItems'] = noOfCheckedResults / noOfResults


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
    githubTotalAPKWithTags = 0
    githubTotalAPKWithoutTags = 0
    googleTotalAPKWithTags = 0
    githubTotalPKWithTags = 0
    githubTotalPKWithoutTags = 0
    googleTotalPKWithTags = 0

    githubTotalRecallWithTags = 0
    githubTotalRecallWithoutTags = 0
    googleTotalRecallWithTags = 0

    for key in userData:
        avg = 0
        githubWithoutTagsAPK = 0
        googleAPK = 0
        githubWithTagsAPK = 0

        githubWithoutTagsPK = 0
        googlePK = 0
        githubWithTagsPK = 0

        githubWithoutTagsRecall = 0
        googleRecall = 0
        githubWithTagsRecall = 0

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

            userStatistics[key][id]['APKGithubWithTags'] = getAPK(
                userData[key][i].ownLinks['links'],
                userData[key][i].ownPreferences['checked']) if len(
                userData[key][i].ownLinks['links']) > 0 else 0

            # compute P@K for each technique
            userStatistics[key][id]['PKGithubWithoutTags'] = getPrecisionK(
                userData[key][i].githubLinks['github']['links'],
                userData[key][i].githubPreferences['github']['checked'])

            userStatistics[key][id]['PKGoogle'] = getPrecisionK(
                userData[key][i].githubLinks['google']['links'],
                userData[key][i].githubPreferences['google']['checked'])

            userStatistics[key][id]['PKGithubWithTags'] = getPrecisionK(
                userData[key][i].ownLinks['links'],
                userData[key][i].ownPreferences['checked'])

            # compute Recall@K for each technique
            userStatistics[key][id]['RecallGithubWithoutTags'] = getRecallK(
                userData[key][i].githubLinks['github']['links'],
                userData[key][i].githubPreferences['github']['checked'])

            userStatistics[key][id]['RecallGoogle'] = getRecallK(
                userData[key][i].githubLinks['google']['links'],
                userData[key][i].githubPreferences['google']['checked'])

            userStatistics[key][id]['RecallGithubWithTags'] = getRecallK(
                userData[key][i].ownLinks['links'],
                userData[key][i].ownPreferences['checked'])

            if 'valid' in userData[key][i].githubLinks['google'] and not userData[key][i].githubLinks['google'][
                'valid']:
                googleInvalidCount += 1

            githubWithoutTagsAPK += userStatistics[key][id]['APKGithubWithoutTags']
            githubWithTagsAPK += userStatistics[key][id]['APKGithubWithTags']
            googleAPK += userStatistics[key][id]['APKGoogle']

            githubWithoutTagsPK += userStatistics[key][id]['PKGithubWithoutTags']
            githubWithTagsPK += userStatistics[key][id]['PKGithubWithTags']
            googlePK += userStatistics[key][id]['PKGoogle']

            githubWithoutTagsRecall += userStatistics[key][id]['RecallGithubWithoutTags']
            githubWithTagsRecall += userStatistics[key][id]['RecallGithubWithTags']
            googleRecall += userStatistics[key][id]['RecallGoogle']

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

        # APK
        userStatistics[key]['githubWithTagsAPKAverage'] = githubWithTagsAPK / len(userData[key])
        userStatistics[key]['githubWithoutTagsAPKAverage'] = githubWithoutTagsAPK / len(userData[key])
        userStatistics[key]['googleAPKAverage'] = googleAPK / (len(userData[key]) - googleInvalidCount) if (len(
            userData[key]) - googleInvalidCount) > 0 else 1

        # PK
        userStatistics[key]['githubWithTagsPKAverage'] = githubWithTagsPK / len(userData[key])
        userStatistics[key]['githubWithoutTagsPKAverage'] = githubWithoutTagsPK / len(userData[key])
        userStatistics[key]['googlePKAverage'] = googlePK / (len(userData[key]) - googleInvalidCount) if (len(
            userData[key]) - googleInvalidCount) > 0 else 1

        # Recall
        userStatistics[key]['githubWithTagsRecallAverage'] = githubWithTagsPK / len(userData[key])
        userStatistics[key]['githubWithoutTagsRecallAverage'] = githubWithoutTagsPK / len(userData[key])
        userStatistics[key]['googleRecallAverage'] = googlePK / (len(userData[key]) - googleInvalidCount) if (len(
            userData[key]) - googleInvalidCount) > 0 else 1

        # APK
        githubTotalAPKWithTags += userStatistics[key]['githubWithTagsAPKAverage']
        githubTotalAPKWithoutTags += userStatistics[key]['githubWithoutTagsAPKAverage']
        googleTotalAPKWithTags += userStatistics[key]['googleAPKAverage']

        # PK
        githubTotalPKWithTags += userStatistics[key]['githubWithTagsPKAverage']
        githubTotalPKWithoutTags += userStatistics[key]['githubWithoutTagsPKAverage']
        googleTotalPKWithTags += userStatistics[key]['googlePKAverage']

        githubTotalRecallWithTags += userStatistics[key]['githubWithTagsPKAverage']
        githubTotalRecallWithoutTags += userStatistics[key]['githubWithoutTagsPKAverage']
        googleTotalRecallWithTags += userStatistics[key]['googlePKAverage']

        totalAvg += avg

    userStatistics['totalAverageTimeSpentOnEvaluation'] = convertInTime(totalAvg / len(userData.keys()))

    searchStatistics = getSearchResultsStatistics(data)

    scenarioAvg = {}

    for key in scenarioStatistics:
        scenarioAvg[key] = {'searchWithTags': {'github': {'APK': [], 'PK': [], 'RecallK': []},
                                               'google': {'APK': [], 'PK': [], 'RecallK': []}},
                            'searchWithoutTags': {'github': {'APK': [], 'PK': [], 'RecallK': []}}}

        scenarioStatistics[key]['averageTime'] = convertInTime(
            scenarioStatistics[key]['averageTime'] / scenarioStatistics[key]['noOfAnswers'])
        # MAPK
        searchStatistics['searchWithTags']['github']['MAPK'] = githubTotalAPKWithTags / scenarioStatistics[key][
            'noOfAnswers']
        searchStatistics['searchWithTags']['google']['MAPK'] = googleTotalAPKWithTags / scenarioStatistics[key][
            'noOfAnswersGoogleValid']
        searchStatistics['searchWithoutTags']['github']['MAPK'] = githubTotalAPKWithoutTags / scenarioStatistics[key][
            'noOfAnswers']
        # AVERAGEPK (MAPK2)
        searchStatistics['searchWithTags']['github']['AveragePK'] = githubTotalPKWithTags / scenarioStatistics[key][
            'noOfAnswers']
        searchStatistics['searchWithTags']['google']['AveragePK'] = googleTotalPKWithTags / scenarioStatistics[key][
            'noOfAnswersGoogleValid']
        searchStatistics['searchWithoutTags']['github']['AveragePK'] = githubTotalPKWithoutTags / \
                                                                       scenarioStatistics[key][
                                                                           'noOfAnswers']
        # AverageRecall
        searchStatistics['searchWithTags']['github']['AverageRecall'] = githubTotalRecallWithTags / \
                                                                        scenarioStatistics[key][
                                                                            'noOfAnswers']
        searchStatistics['searchWithTags']['google']['AverageRecall'] = googleTotalRecallWithTags / \
                                                                        scenarioStatistics[key][
                                                                            'noOfAnswersGoogleValid']
        searchStatistics['searchWithoutTags']['github']['AverageRecall'] = githubTotalRecallWithoutTags / \
                                                                           scenarioStatistics[key][
                                                                               'noOfAnswers']
    # build statistics per scenario based on user scenario
    for key in userData:
        for i in range(0, len(userData[key])):
            id = userData[key][i].extraInfo['scenarioId']

            #APK
            scenarioAvg[id]['searchWithoutTags']['github']['APK'].append(userStatistics[key][id]['APKGithubWithoutTags'])

            if not('valid' in userData[key][i].githubLinks['google'] and not userData[key][i].githubLinks['google'][
                'valid']):
                scenarioAvg[id]['searchWithTags']['google']['APK'].append(userStatistics[key][id]['APKGoogle'])

            scenarioAvg[id]['searchWithTags']['github']['APK'].append(userStatistics[key][id]['APKGithubWithTags'])

            #PK
            scenarioAvg[id]['searchWithoutTags']['github']['PK'].append(userStatistics[key][id]['PKGithubWithoutTags'])

            if not ('valid' in userData[key][i].githubLinks['google'] and not userData[key][i].githubLinks['google'][
                'valid']):
                scenarioAvg[id]['searchWithTags']['google']['PK'].append(userStatistics[key][id]['PKGoogle'])

            scenarioAvg[id]['searchWithTags']['github']['PK'].append(userStatistics[key][id]['PKGithubWithTags'])

            #RecallK
            scenarioAvg[id]['searchWithoutTags']['github']['RecallK'].append(userStatistics[key][id]['RecallGithubWithoutTags'])

            if not ('valid' in userData[key][i].githubLinks['google'] and not userData[key][i].githubLinks['google'][
                'valid']):
                scenarioAvg[id]['searchWithTags']['google']['RecallK'].append(userStatistics[key][id]['RecallGoogle'])

            scenarioAvg[id]['searchWithTags']['github']['RecallK'].append(userStatistics[key][id]['RecallGithubWithTags'])

    #build scenario averages
    for key in userData:
        for i in range(0, len(userData[key])):
            id = userData[key][i].extraInfo['scenarioId']
            scenarioStatistics[id]['githubWithoutTagsMAPK'] = np.mean(scenarioAvg[id]['searchWithoutTags']['github']['APK'])
            scenarioStatistics[id]['githubWithTagsMAPK'] = np.mean(scenarioAvg[id]['searchWithTags']['github']['APK'])
            scenarioStatistics[id]['googleWithTagsMAPK'] = np.mean(scenarioAvg[id]['searchWithTags']['google']['APK'])

            scenarioStatistics[id]['githubWithoutTagsAveragePK'] = np.mean(scenarioAvg[id]['searchWithoutTags']['github']['PK'])
            scenarioStatistics[id]['githubWithTagsAveragePK'] = np.mean(scenarioAvg[id]['searchWithTags']['github']['PK'])
            scenarioStatistics[id]['googleWithTagsAveragePK'] = np.mean(scenarioAvg[id]['searchWithTags']['google']['PK'])

            scenarioStatistics[id]['githubWithoutTagsAverageRecallK'] = np.mean(scenarioAvg[id]['searchWithoutTags']['github']['RecallK'])
            scenarioStatistics[id]['githubWithTagsAverageRecallK'] = np.mean(scenarioAvg[id]['searchWithTags']['github']['RecallK'])
            scenarioStatistics[id]['googleWithTagsAverageRecallK'] = np.mean(scenarioAvg[id]['searchWithTags']['google']['RecallK'])


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
