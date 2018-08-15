#!python
from __future__ import print_function
import mlbgame
import lxml.etree as etree
import mlbgame.data
import mlbgame.object
import mlbgame.stats
import time
import datetime
from datetime import datetime, timedelta, timezone
from mlbgame.events import Inning
from mlbgame.events import AtBat
from pyfcm import FCMNotification
import twitter

DST = timezone(timedelta(hours=-7), 'DST')
d_today = datetime.now(DST)
y = d_today.year
m = d_today.month
d = d_today.day
h = d_today.hour
#H/A [0]or[1] [yy/mm/dd]
t0=time.time()
for i in range(45):
        t1=time.time()
        try:
            game = mlbgame.day(y, m, d, home='Angels', away='Angels')[0]
            stats = mlbgame.player_stats(game.game_id)
        except ValueError:
            t2=time.time()
            t3=t2-t1
            time.sleep(19-t3)
        except IndexError:
            t2=time.time()
            t3=t2-t1
            time.sleep(19-t3)
        else :
                #H/A flag 0:away 1:home
                str1=str(game)
                slice=str1[0:6]

                if slice=="Angels":
                  HAflag=0
                else:
                  HAflag=1

                 # get data from data module
                box_score = mlbgame.data.get_box_score(game.game_id)
                # parse XML
                box_score_tree = etree.parse(box_score).getroot()
                # get batting info
                batting = box_score_tree.findall('batting')
                def __player_stats_info(data, name):
                    home = []
                    away = []
                    for y in data:
                        # loops through pitchers and batters
                        for x in y.findall(name):
                            stats = {}
                            # loop through and save stats
                            for i in x.attrib:
                                stats[i] = x.attrib[i]
                            # apply to correct list
                            if y.attrib['team_flag'] == 'home':
                                home.append(stats)
                            else:
                                away.append(stats)
                    return (home, away)
                #get ids
                batting_info = __player_stats_info(batting, 'batter')
                if HAflag==0:
                    info = batting_info[1]
                else   :
                   info = batting_info[0] #home:0 away:1
                ids=[]
                infobo='0'
                battingorder=0
                prebo=0
                for a in range(len(info)):
                        infoa = info[a]
                        ida=infoa['id']
                        if ida=='660271' :
                            infobo = infoa['bo']
                            abo = int(infoa['ab'])+int(infoa['bb'])+1
                            bo = infobo[:1] #battingorder first number 
                            ph = int(infobo[2:3]) #if he is not PH, ph = 0
                            battingorder=int(bo)
                            if battingorder==1:
                                prebo=9
                            else :
                                prebo=battingorder-1

                print(infobo)
                print(battingorder)
                

                #last event
                data = mlbgame.data.get_game_events(game.game_id)
                parsed = etree.parse(data)
                root = parsed.getroot()
                output={}
                innings = root.findall('inning')
                def __inning_info(inning, part):
                    # info
                    info = []
                    # loop through the half
                    half = inning.findall(part)[0]
                    for y in half.findall('atbat'):
                        atbat = {}
                        # loop through and save info
                        for i in y.attrib:
                            atbat[i] = y.attrib[i]
                        info.append(atbat)
                    return info
                for x in innings:
                        output[x.attrib['num']] = {
                            'top': __inning_info(x, 'top'),
                            'bottom': __inning_info(x, 'bottom')
                        }
                #get lastbatter id
                lastbatter=0
                o0 = len(output)
                o1 = output['%s' % o0] 
                eo='0'
                if HAflag==0:
                    try : 
                        er = o1['bottom']
                        err = len(er)-1
                        errr = er[err]
                    except IndexError:
                        pass
                    else :
                        e = o1['bottom']
                        e1 = len(e)-1
                        e2 = e[e1]
                        eo = e2['o']
                    finally :
                        o2 = o1['top']
                        if len(o2)!=0:
                            o3 = len(o2)-1
                            o4 = o2[o3]
                            lastbatter = int(o4['batter'])
                            if lastbatter==660271:
                                sevent=o4['event']
                                timelog=o4['start_tfs']
                                timelogh=int(timelog[:2])
                                timelogm=int(timelog[2:4])
                                if timelogh>=15:
                                    timelogh=timelogh-15
                                else:
                                    timelogh=timelogh+9
                                comment="打席結果:{0}({1}時{2}分)".format(sevent,timelogh,timelogm)
                                abo=abo+1
                                # api = twitter.Api(consumer_key="",consumer_secret="",access_token_key="",access_token_secret="")
                                # api.PostUpdate(comment)
                                # push_service = FCMNotification(api_key="")
                                # message = comment
                                # result = push_service.notify_topic_subscribers(topic_name="result", message_body=message)
                                break
                            outcount = o4['o'] 
                if HAflag==1:
                    try :
                        er = o1['bottom']
                        err = len(er)-1
                        errr = er[err]
                    except IndexError:
                        e = o1['top']
                        e1 = len(e)-1
                        if len(e)==0:
                            e0='0'
                        else :
                            e2 = e[e1]
                            eo = e2['o']
                        try:
                            o0 = o0-1
                            o1 = output['%s' % o0] 
                            o2 = o1['bottom']
                            o3 = len(o2)-1
                            o4 = o2[o3]
                        except IndexError:
                            pass 
                        except KeyError:
                            pass
                        else :
                            lastbatter = int(o4['batter'])
                            endflag=0
                            if HAflag==1 and eo=='3':
                                endoutput = o1['top']
                                endoutput1 = len(endoutput)-1
                                endoutput2 = endoutput[endoutput1]
                                homerunp = endoutput2['home_team_runs']
                                awayrunp = endoutput2['away_team_runs']
                                homerunpi = int(homerunp)
                                awayrunpi = int(awayrunp)
                                if o0>=9 and homerunpi>awayrunpi:
                                    endflag=1
                            if lastbatter==660271 and endflag==0:
                                sevent=o4['event']
                                timelog=o4['start_tfs']
                                timelogh=int(timelog[:2])
                                timelogm=int(timelog[2:4])
                                if timelogh>=15:
                                    timelogh=timelogh-15
                                else:
                                    timelogh=timelogh+9
                                # comment="打席結果:{0}({1}時{2}分)".format(sevent,timelogh,timelogm)
                                # abo=abo+1
                                # api = twitter.Api(consumer_key="",consumer_secret="",access_token_key="",access_token_secret="")
                                # api.PostUpdate(comment)
                                # push_service = FCMNotification(api_key="")
                                # message = comment
                                # result = push_service.notify_topic_subscribers(topic_name="result", message_body=message)
                            outcount = o4['o']
                    else :
                        o2 = o1['bottom']
                        o3 = len(o2)-1
                        o4 = o2[o3]
                        lastbatter = int(o4['batter'])
                        endflag=0
                        homerunp = o4['home_team_runs']
                        awayrunp = o4['away_team_runs']
                        homerunpi = int(homerunp)
                        awayrunpi = int(awayrunp)
                        if o0>=9 and homerunpi>awayrunpi:
                            endflag=1
                        if lastbatter==660271 and endflag==0:
                            sevent=o4['event']
                            timelog=o4['start_tfs']
                            timelogh=int(timelog[:2])
                            timelogm=int(timelog[2:4])
                            if timelogh>=15:
                                timelogh=timelogh-15
                            else:
                                timelogh=timelogh+9
                            # comment="打席結果:{0}({1}時{2}分)".format(sevent,timelogh,timelogm)
                            # abo=abo+1
                            # api = twitter.Api(consumer_key="",consumer_secret="",access_token_key="",access_token_secret="")
                            # api.PostUpdate(comment)
                            # push_service = FCMNotification(api_key="")
                            # message = comment
                            # result = push_service.notify_topic_subscribers(topic_name="result", message_body=message)
                            # break
                        outcount = o4['o']
                        eo='0'
                preboo=0
                for a in range(len(info)):
                    preinfo = info[a]
                    preid=int(preinfo['id'])
                    if  preid==lastbatter :
                        prebattingorder = preinfo['bo']
                        prebattingorder1 =prebattingorder[:1] 
                        preboo=int(prebattingorder1)
                endflag=0
                if HAflag==1 and eo=='3':
                    endoutput = o1['top']
                    endoutput1 = len(endoutput)-1
                    endoutput2 = endoutput[endoutput1]
                    homerunp = endoutput2['home_team_runs']
                    awayrunp = endoutput2['away_team_runs']
                    homerunpi = int(homerunp)
                    awayrunpi = int(awayrunp)
                    if o0>=9 and homerunpi>awayrunpi:
                        endflag=1
                if HAflag==1:
                        homerunp = o4['home_team_runs']
                        awayrunp = o4['away_team_runs']
                        homerunpi = int(homerunp)
                        awayrunpi = int(awayrunp)
                        if o0>=9 and homerunpi>awayrunpi:
                            endflag=1

                Showflag=0
                if prebo==preboo and (outcount=='0' or outcount=='1' or outcount=='2'):
                    if abo==1 or ph ==0:
                        Showflag=1
                if prebo==preboo and outcount=='3':
                    if eo=='3' and endflag==0:
                        if abo==1 or ph ==0:
                            Showflag=1
                if Showflag==1:
                    ###push dohere
                    push_service = FCMNotification(api_key="")
                    message = "It's Shotime!"
                    result = push_service.notify_topic_subscribers(topic_name="show", message_body=message)
                    result = push_service.notify_topic_subscribers(topic_name="result", message_body=message)
                    api = twitter.Api(consumer_key="",consumer_secret="",access_token_key="",access_token_secret="")
                    if ph==0:
                        api.PostUpdate("さぁ大谷だ！("+str(abo)+"打席目)")
                    if ph!=0:
                        api.PostUpdate("さぁ大谷だ！(代打)")
                    t4=time.time()
                    t5=int((900-t4+t0)/15)
                    Flag=0
                    if t5 >=1:
                        for i in range(t5):
                            t6=time.time()
                            sho=0
                            data = mlbgame.data.get_game_events(game.game_id)
                            parsed = etree.parse(data)
                            root = parsed.getroot()
                            output={}
                            innings = root.findall('inning')
                            def __inning_info(inning, part):
                                # info
                                info = []
                                # loop through the half
                                half = inning.findall(part)[0]
                                for y in half.findall('atbat'):
                                    atbat = {}
                                    # loop through and save info
                                    for i in y.attrib:
                                        atbat[i] = y.attrib[i]
                                    info.append(atbat)
                                return info
                            for x in innings:
                                    output[x.attrib['num']] = {
                                        'top': __inning_info(x, 'top'),
                                        'bottom': __inning_info(x, 'bottom')
                                    }
                                    lastbatter=0
                                    o0 = len(output)
                                    o1 = output['%s' % o0]
                                    if HAflag==0:
                                        try : 
                                            er = o1['bottom']
                                            err = len(er)-1
                                            errr = er[err]
                                        except IndexError:
                                            pass
                                        finally :
                                            o2 = o1['top']
                                            o3 = len(o2)-1
                                            o4 = o2[o3]
                                            lastbatter = int(o4['batter'])
                                            if lastbatter==660271:
                                                sho = 1
                                                sevent=o4['event']
                                    if HAflag==1:
                                        try :
                                            er = o1['bottom']
                                            err = len(er)-1
                                            errr = er[err]
                                        except IndexError:
                                            try:
                                                o0 = o0-1
                                                o1 = output['%s' % o0] 
                                                o2 = o1['bottom']
                                                o3 = len(o2)-2
                                                o4 = o2[o3]
                                            except IndexError:
                                                pass 
                                            except KeyError:
                                                pass
                                            else :
                                                lastbatter = int(o4['batter'])
                                                if lastbatter==660271:
                                                    sho = 1
                                                    sevent = o4['event']
                                        else :
                                            o2 = o1['bottom']
                                            o3 = len(o2)-1
                                            o4 = o2[o3]
                                            lastbatter = int(o4['batter'])
                                            if lastbatter==660271:
                                                sho = 1
                                                sevent = o4['event']
                            if sho==1:
                                timelog=o4['start_tfs']
                                timelogh=int(timelog[:2])
                                timelogm=int(timelog[2:4])
                                if timelogh>=15:
                                    timelogh=timelogh-15
                                else:
                                    timelogh=timelogh+9
                                # comment="打席結果:{0}({1}時{2}分)".format(sevent,timelogh,timelogm)
                                # abo=abo+1
                                # api = twitter.Api(consumer_key="",consumer_secret="",access_token_key="",access_token_secret="")
                                # api.PostUpdate(comment)
                                # push_service = FCMNotification(api_key="")
                                # message = comment
                                # result = push_service.notify_topic_subscribers(topic_name="result", message_body=message)
                                Flag=1
                                break
                            t7=time.time()
                            t8=t7-t6
                            print(sho)
                            time.sleep(15-t8)
                    else:
                        break
                    if Flag==1:
                        break

                    
        t2=time.time()
        t3=t2-t1
        print(t3)
        time.sleep(20-t3)    