"""
AWS DeepRacer reward function
"""
import math
import time
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import LinearRing, LineString
from numpy import array

OVAL_TRACK_RACE_LINE = \
array([[2.77202313, 0.86236633],
       [2.96151437, 0.81752476],
       [3.15574541, 0.77947957],
       [3.35401022, 0.74758153],
       [3.5557018 , 0.72122517],
       [3.76029509, 0.69984402],
       [3.96733538, 0.68291194],
       [4.17642814, 0.66994281],
       [4.38726719, 0.66057006],
       [4.59958755, 0.65448141],
       [4.81320483, 0.65170448],
       [5.02722982, 0.65270569],
       [5.23958941, 0.6578628 ],
       [5.44976863, 0.66755716],
       [5.65735175, 0.68220305],
       [5.86193859, 0.70218515],
       [6.06314116, 0.72784067],
       [6.26058454, 0.75945803],
       [6.45390955, 0.79727605],
       [6.64273788, 0.84153424],
       [6.82657755, 0.89258713],
       [7.00490098, 0.95077319],
       [7.17718147, 1.01636738],
       [7.3425877 , 1.08992087],
       [7.50023223, 1.17190876],
       [7.64898651, 1.2628922 ],
       [7.78738344, 1.36351699],
       [7.91347317, 1.47447354],
       [8.02463565, 1.59632745],
       [8.11740041, 1.72905762],
       [8.19290898, 1.86962197],
       [8.25240687, 2.01571858],
       [8.2966585 , 2.16569229],
       [8.32643788, 2.31818976],
       [8.34223358, 2.47212347],
       [8.34443684, 2.6265478 ],
       [8.33333198, 2.78060814],
       [8.30891149, 2.93346852],
       [8.27061579, 3.08415975],
       [8.21785392, 3.23154487],
       [8.14927546, 3.37400838],
       [8.06326302, 3.50929051],
       [7.95756464, 3.63381225],
       [7.83754528, 3.7486062 ],
       [7.70510392, 3.85376707],
       [7.56156523, 3.94936186],
       [7.40816933, 4.03565557],
       [7.24586525, 4.11284122],
       [7.07554311, 4.18119668],
       [6.89812063, 4.24117074],
       [6.71436961, 4.29316522],
       [6.52507976, 4.33771344],
       [6.33104579, 4.37547577],
       [6.13297695, 4.40711235],
       [5.9314893 , 4.43325121],
       [5.72711442, 4.45447949],
       [5.52030763, 4.47133618],
       [5.31145501, 4.48430194],
       [5.10078344, 4.49344392],
       [4.88920292, 4.49869714],
       [4.67926187, 4.4999895 ],
       [4.47331831, 4.49732951],
       [4.27196051, 4.49078664],
       [4.0749199 , 4.48034629],
       [3.88171517, 4.46594003],
       [3.69194877, 4.44740695],
       [3.50531615, 4.42456111],
       [3.32161743, 4.39720122],
       [3.14075692, 4.36510565],
       [2.96275316, 4.32799753],
       [2.78773102, 4.28554112],
       [2.61599079, 4.23721767],
       [2.44792457, 4.18250188],
       [2.28410845, 4.1207434 ],
       [2.12531583, 4.05121276],
       [1.97244988, 3.97326162],
       [1.82705025, 3.88575605],
       [1.6909193 , 3.78780905],
       [1.56641859, 3.67860987],
       [1.45654372, 3.5576907 ],
       [1.36508965, 3.42535446],
       [1.29004027, 3.28537095],
       [1.23061846, 3.13981959],
       [1.18610649, 2.99033135],
       [1.15603146, 2.83819726],
       [1.13997112, 2.68451764],
       [1.13756347, 2.53025017],
       [1.14876101, 2.37627731],
       [1.17362963, 2.22349628],
       [1.21247633, 2.07289195],
       [1.26565315, 1.92555855],
       [1.33451394, 1.78308875],
       [1.42058923, 1.64766266],
       [1.52615003, 1.52277742],
       [1.64612036, 1.40758224],
       [1.77876545, 1.30215813],
       [1.92270231, 1.20645223],
       [2.0766165 , 1.12017207],
       [2.23943428, 1.04301758],
       [2.41019805, 0.9746333 ],
       [2.58800581, 0.91457886],
       [2.77202313, 0.86236633]])
# END OVAL_TRACK_RACE_LINE

# a.k.a. Virtual_May19_Train_track
LONDON_LOOP_RACE_LINE = \
        array([[5.19098353, 0.65866346],
       [5.27520689, 0.63272276],
       [5.35838489, 0.61227744],
       [5.44036556, 0.59766022],
       [5.52100331, 0.58905348],
       [5.6001574 , 0.58652996],
       [5.67769325, 0.5900787 ],
       [5.75348326, 0.59962956],
       [5.82740688, 0.61507409],
       [5.8993538 , 0.63627226],
       [5.96922693, 0.66305826],
       [6.03694176, 0.69525365],
       [6.10244066, 0.73264318],
       [6.16568751, 0.77500023],
       [6.22668108, 0.8220677 ],
       [6.28546243, 0.87355625],
       [6.34212532, 0.92913825],
       [6.39682356, 0.98844984],
       [6.44978186, 1.05109129],
       [6.50129783, 1.11665797],
       [6.55176196, 1.18475363],
       [6.60165068, 1.25500867],
       [6.65143753, 1.32697048],
       [6.70198186, 1.4006523 ],
       [6.75259931, 1.4742827 ],
       [6.80329071, 1.54786113],
       [6.85405685, 1.62138701],
       [6.9049053 , 1.69485502],
       [6.95454751, 1.7672823 ],
       [7.002279  , 1.83914464],
       [7.04751983, 1.91096115],
       [7.08970174, 1.9831155 ],
       [7.12824629, 2.05582472],
       [7.16263354, 2.129191  ],
       [7.1924168 , 2.20323863],
       [7.21722663, 2.27793227],
       [7.23676069, 2.35318855],
       [7.25078474, 2.42888403],
       [7.2591084 , 2.50486408],
       [7.26160571, 2.58094831],
       [7.25819103, 2.65693825],
       [7.24880109, 2.73262085],
       [7.2334138 , 2.80777242],
       [7.21205187, 2.88216422],
       [7.1847716 , 2.95556571],
       [7.15168475, 3.02775329],
       [7.11294285, 3.09851319],
       [7.06876016, 3.16765322],
       [7.01941883, 3.23501394],
       [6.9652639 , 3.30047701],
       [6.9067089 , 3.36397809],
       [6.84423547, 3.42551951],
       [6.77838149, 3.48517782],
       [6.70972119, 3.54310482],
       [6.63884837, 3.59952679],
       [6.56635538, 3.6547371 ],
       [6.49281836, 3.70908879],
       [6.4187907 , 3.76298294],
       [6.34470987, 3.81680448],
       [6.27058217, 3.87056022],
       [6.19640969, 3.92425304],
       [6.12212641, 3.97774048],
       [6.04756388, 4.03060672],
       [5.97257428, 4.08243721],
       [5.89702816, 4.13282984],
       [5.82081841, 4.18140471],
       [5.74386233, 4.22781316],
       [5.6661019 , 4.27174555],
       [5.58750164, 4.31293316],
       [5.50804506, 4.35114528],
       [5.42773515, 4.38620017],
       [5.34659152, 4.41796615],
       [5.26464369, 4.44634483],
       [5.18193319, 4.4712887 ],
       [5.0985069 , 4.49278082],
       [5.0144188 , 4.51085137],
       [4.9297263 , 4.52556874],
       [4.84448868, 4.5370407 ],
       [4.7587661 , 4.54542039],
       [4.67261524, 4.5508953 ],
       [4.58608836, 4.55370335],
       [4.49923057, 4.55413608],
       [4.41208038, 4.5525389 ],
       [4.3246732 , 4.54928735],
       [4.23704863, 4.54476604],
       [4.14925831, 4.53936432],
       [4.06136928, 4.53347524],
       [3.97210333, 4.52739643],
       [3.88281603, 4.52148913],
       [3.79349506, 4.51584723],
       [3.70413021, 4.51054303],
       [3.61471456, 4.50561901],
       [3.52524503, 4.50108703],
       [3.43572198, 4.49693384],
       [3.34614884, 4.49312634],
       [3.25653105, 4.48961998],
       [3.16687539, 4.48636333],
       [3.07718827, 4.48330483],
       [2.98746903, 4.4803956 ],
       [2.89670118, 4.47756041],
       [2.80593134, 4.47451583],
       [2.7151768 , 4.47111559],
       [2.62444407, 4.46721645],
       [2.53373968, 4.46268268],
       [2.44307028, 4.45738675],
       [2.35244295, 4.45120561],
       [2.26186536, 4.44402189],
       [2.17134599, 4.43572361],
       [2.08089452, 4.42620267],
       [1.99052256, 4.41535118],
       [1.9002445 , 4.40306123],
       [1.81007932, 4.38922087],
       [1.72005397, 4.37371785],
       [1.6303881 , 4.35625552],
       [1.54228323, 4.33646155],
       [1.45695464, 4.3141337 ],
       [1.37488472, 4.28906695],
       [1.29627239, 4.26109292],
       [1.22119542, 4.23008238],
       [1.14967215, 4.19594426],
       [1.08169468, 4.15861756],
       [1.01725101, 4.11805986],
       [0.9563274 , 4.074248  ],
       [0.89891908, 4.02716881],
       [0.84502959, 3.97681922],
       [0.79466884, 3.9232072 ],
       [0.74785582, 3.86634815],
       [0.7046179 , 3.80626469],
       [0.66498681, 3.74298945],
       [0.62899017, 3.67657135],
       [0.5966554 , 3.60707105],
       [0.56798535, 3.53457953],
       [0.54296935, 3.45920618],
       [0.52155814, 3.38109553],
       [0.50366788, 3.3004197 ],
       [0.48915909, 3.21738865],
       [0.47783328, 3.13224584],
       [0.46942191, 3.04526803],
       [0.46358508, 2.95675783],
       [0.45991905, 2.86703127],
       [0.45796136, 2.77640784],
       [0.45720489, 2.68519564],
       [0.45710927, 2.5936715 ],
       [0.45712028, 2.50209918],
       [0.45722301, 2.41053408],
       [0.45782291, 2.31904099],
       [0.45937169, 2.22769891],
       [0.46231441, 2.1366026 ],
       [0.4670852 , 2.04586435],
       [0.47409908, 1.95561347],
       [0.48374806, 1.86599602],
       [0.49639555, 1.77717402],
       [0.51238494, 1.68932863],
       [0.5320218 , 1.6026563 ],
       [0.55558062, 1.51737155],
       [0.58330081, 1.43370717],
       [0.61539834, 1.35192186],
       [0.65204117, 1.27229348],
       [0.69335884, 1.19512675],
       [0.73943326, 1.12075381],
       [0.79029549, 1.04953862],
       [0.84590136, 0.98186545],
       [0.90613532, 0.91814212],
       [0.97079272, 0.858781  ],
       [1.03958172, 0.80418461],
       [1.11212183, 0.75471219],
       [1.18796922, 0.71066312],
       [1.26664021, 0.67225222],
       [1.34764591, 0.63960708],
       [1.43051667, 0.61275969],
       [1.51482624, 0.59166287],
       [1.60020402, 0.57620973],
       [1.68633795, 0.5662553 ],
       [1.77296925, 0.56161193],
       [1.85988879, 0.56207074],
       [1.94692979, 0.56742122],
       [2.0339599 , 0.57743427],
       [2.1208763 , 0.59186679],
       [2.20760038, 0.61047766],
       [2.29407384, 0.63301834],
       [2.38025639, 0.65922563],
       [2.46612277, 0.68882936],
       [2.55166099, 0.72154157],
       [2.63686787, 0.75705674],
       [2.72173467, 0.79505408],
       [2.80606272, 0.83509449],
       [2.88993504, 0.87272516],
       [2.97424245, 0.90802894],
       [3.05881103, 0.94061931],
       [3.14348999, 0.97016858],
       [3.22816338, 0.99642219],
       [3.3127539 , 1.01918429],
       [3.39722109, 1.0383179 ],
       [3.48155608, 1.05372464],
       [3.56577547, 1.06534325],
       [3.64991465, 1.07314328],
       [3.7340213 , 1.07711128],
       [3.8181503 , 1.07724548],
       [3.90235922, 1.07356838],
       [3.98670503, 1.06610907],
       [4.07124146, 1.0549134 ],
       [4.1560166 , 1.04004837],
       [4.24107212, 1.02159405],
       [4.32644186, 0.99965295],
       [4.41215017, 0.97435958],
       [4.49821285, 0.94586809],
       [4.58463518, 0.9143692 ],
       [4.67141267, 0.88008357],
       [4.75853155, 0.84325971],
       [4.84596897, 0.80417604],
       [4.93369332, 0.76314412],
       [5.02005007, 0.7247285 ],
       [5.10587254, 0.68959061],
       [5.19098353, 0.65866346]])

MEXICO_TRACK_RACE_LINE = \
array([[ 6.28218173,  2.59105723],
       [ 6.1757048 ,  2.6012493 ],
       [ 6.0682997 ,  2.60885282],
       [ 5.96012511,  2.61419801],
       [ 5.85132868,  2.61763146],
       [ 5.74204721,  2.61951135],
       [ 5.63240599,  2.62019837],
       [ 5.522531  ,  2.62008946],
       [ 5.41254135,  2.6195837 ],
       [ 5.30223501,  2.61911454],
       [ 5.19194367,  2.61875592],
       [ 5.08167541,  2.61856741],
       [ 4.97144021,  2.61862185],
       [ 4.86124717,  2.61898545],
       [ 4.75110455,  2.61971742],
       [ 4.64101782,  2.62085596],
       [ 4.53098954,  2.62241746],
       [ 4.4210223 ,  2.62441788],
       [ 4.31111665,  2.62685803],
       [ 4.20127546,  2.62975467],
       [ 4.09149846,  2.6331016 ],
       [ 3.98207569,  2.6369074 ],
       [ 3.87370934,  2.63983166],
       [ 3.76565874,  2.64153234],
       [ 3.65784568,  2.64165467],
       [ 3.55036403,  2.63984239],
       [ 3.44336381,  2.63573696],
       [ 3.33702758,  2.62902053],
       [ 3.23158536,  2.61935928],
       [ 3.12731533,  2.60642775],
       [ 3.02453981,  2.5899282 ],
       [ 2.92362012,  2.56959613],
       [ 2.82493114,  2.54523076],
       [ 2.7287954 ,  2.51676622],
       [ 2.6353556 ,  2.48439774],
       [ 2.54483305,  2.44817756],
       [ 2.45745454,  2.40815239],
       [ 2.37361981,  2.36419398],
       [ 2.29381409,  2.31615348],
       [ 2.21859877,  2.26389406],
       [ 2.14871319,  2.20723622],
       [ 2.0848547 ,  2.14617057],
       [ 2.0278434 ,  2.08074457],
       [ 1.97811527,  2.01135424],
       [ 1.93632144,  1.9383616 ],
       [ 1.90268754,  1.86237487],
       [ 1.87789395,  1.78389623],
       [ 1.86271009,  1.7035661 ],
       [ 1.85882856,  1.62226677],
       [ 1.86601798,  1.54135099],
       [ 1.88302137,  1.46183168],
       [ 1.90878344,  1.38433436],
       [ 1.94260541,  1.30932322],
       [ 1.9839263 ,  1.23716618],
       [ 2.03242434,  1.16824297],
       [ 2.08925603,  1.10379464],
       [ 2.15336293,  1.04395499],
       [ 2.22385752,  0.98870833],
       [ 2.29995532,  0.9379279 ],
       [ 2.38097462,  0.89142245],
       [ 2.46627488,  0.84891584],
       [ 2.55534574,  0.81015922],
       [ 2.64769794,  0.77485224],
       [ 2.74287969,  0.74266941],
       [ 2.84044759,  0.71323654],
       [ 2.93997097,  0.6861416 ],
       [ 3.04103796,  0.66094926],
       [ 3.14324922,  0.63720166],
       [ 3.24623171,  0.61444519],
       [ 3.3514923 ,  0.59179272],
       [ 3.45631013,  0.56823646],
       [ 3.5605156 ,  0.54345681],
       [ 3.66394743,  0.51717415],
       [ 3.7664264 ,  0.48910284],
       [ 3.86777917,  0.45900215],
       [ 3.9678239 ,  0.4266517 ],
       [ 4.06637178,  0.39185637],
       [ 4.1632276 ,  0.3544478 ],
       [ 4.25819029,  0.31428381],
       [ 4.35105683,  0.27125011],
       [ 4.44163132,  0.22526634],
       [ 4.52974105,  0.17629717],
       [ 4.61526022,  0.12436871],
       [ 4.6981319 ,  0.06958034],
       [ 4.77837358,  0.01209753],
       [ 4.85588526, -0.04804114],
       [ 4.93055692, -0.11080264],
       [ 5.0021666 , -0.17624519],
       [ 5.07041801, -0.24446774],
       [ 5.13492383, -0.31561204],
       [ 5.19517274, -0.38987235],
       [ 5.25040317, -0.46755653],
       [ 5.29966955, -0.54899771],
       [ 5.3416836 , -0.63459384],
       [ 5.37945646, -0.72245036],
       [ 5.41357953, -0.81217869],
       [ 5.44454567, -0.90345663],
       [ 5.472817  , -0.99597845],
       [ 5.49883623, -1.08945193],
       [ 5.52301503, -1.18361563],
       [ 5.54578556, -1.27823551],
       [ 5.56911395, -1.37045402],
       [ 5.59429751, -1.46119933],
       [ 5.62226953, -1.54968905],
       [ 5.65394097, -1.63510047],
       [ 5.69012196, -1.716606  ],
       [ 5.7315183 , -1.79334737],
       [ 5.77876932, -1.86436383],
       [ 5.83260871, -1.92834333],
       [ 5.89365609, -1.98366246],
       [ 5.96286009, -2.02723409],
       [ 6.03811391, -2.05995023],
       [ 6.1179021 , -2.08258624],
       [ 6.20103008, -2.09577708],
       [ 6.28648872, -2.10006301],
       [ 6.37339139, -2.09593895],
       [ 6.46095081, -2.08388139],
       [ 6.54848009, -2.06447844],
       [ 6.63539704, -2.03818572],
       [ 6.72120181, -2.00546672],
       [ 6.80546419, -1.9667481 ],
       [ 6.88777139, -1.92232151],
       [ 6.96785993, -1.87270234],
       [ 7.04544607, -1.81818136],
       [ 7.12027917, -1.7590371 ],
       [ 7.19213784, -1.69553142],
       [ 7.26082822, -1.62791075],
       [ 7.32618366, -1.55640714],
       [ 7.38806825, -1.48124202],
       [ 7.44638774, -1.40263519],
       [ 7.50110411, -1.32081528],
       [ 7.55224276, -1.23602247],
       [ 7.59989219, -1.14850559],
       [ 7.64419892, -1.0585175 ],
       [ 7.68535807, -0.9663095 ],
       [ 7.72359919, -0.87212434],
       [ 7.75916842, -0.77618825],
       [ 7.79231001, -0.67870349],
       [ 7.82325042, -0.57984364],
       [ 7.85218624, -0.47975352],
       [ 7.87927465, -0.3785562 ],
       [ 7.90462489, -0.27637042],
       [ 7.92829106, -0.17333932],
       [ 7.95026912, -0.0696606 ],
       [ 7.97050383,  0.03440515],
       [ 7.98891441,  0.13856775],
       [ 8.00544018,  0.2425703 ],
       [ 8.01998327,  0.34622076],
       [ 8.03246284,  0.44939863],
       [ 8.04270962,  0.55201382],
       [ 8.050551  ,  0.6540054 ],
       [ 8.05577121,  0.75531513],
       [ 8.05809855,  0.85587174],
       [ 8.05718071,  0.95557726],
       [ 8.05256471,  1.05429543],
       [ 8.04373817,  1.15185464],
       [ 8.0300729 ,  1.24801944],
       [ 8.0108531 ,  1.34247553],
       [ 7.98515327,  1.43473945],
       [ 7.95166919,  1.52395113],
       [ 7.91150386,  1.61008948],
       [ 7.86548384,  1.69315936],
       [ 7.81422559,  1.77315665],
       [ 7.75816885,  1.85003854],
       [ 7.69763979,  1.92372914],
       [ 7.632905  ,  1.99413757],
       [ 7.56413862,  2.0611133 ],
       [ 7.49162537,  2.12462002],
       [ 7.41550561,  2.18450739],
       [ 7.33590906,  2.24061328],
       [ 7.25300312,  2.29282057],
       [ 7.16688105,  2.34092313],
       [ 7.07772114,  2.38482019],
       [ 6.98573893,  2.42447894],
       [ 6.891167  ,  2.45992304],
       [ 6.7942418 ,  2.49122463],
       [ 6.69519612,  2.51849955],
       [ 6.5942552 ,  2.54190426],
       [ 6.49163475,  2.56163311],
       [ 6.38753984,  2.57791529],
       [ 6.28218173,  2.59105723]])

# Constants
DEBUG_LOG_ENABLED = True

# Action space constants
MAX_SPEED = 9
MAX_STEERING_ANGLE = 40.0

# Raceline track
RACE_LINE_WAYPOINTS = MEXICO_TRACK_RACE_LINE 

# TUNING: Adjust these to find tune factors affect on reward
#
# Reward weights, always 0..1.  These are relative to one another
SPEED_FACTOR_WEIGHT = 0.0
SPEED_FACTOR_EASING = 'linear'
WHEEL_FACTOR_WEIGHT = 0.0
WHEEL_FACTOR_EASING = 'linear'
HEADING_FACTOR_WEIGHT = 0.0
HEADING_FACTOR_EASING = 'linear'
STEERING_FACTOR_WEIGHT = 0.0
STEERING_FACTOR_EASING = 'linear'
PROGRESS_FACTOR_WEIGHT = 0.0
PROGRESS_FACTOR_EASING = 'linear'
LANE_FACTOR_WEIGHT = 0.0
LANE_FACTOR_EASING = 'quintic'
RACE_LINE_FACTOR_WEIGHT = 1.0
RACE_LINE_FACTOR_EASING = 'linear'

# Globals
g_last_progress_value = 0.0
g_last_progress_time = 0.0
g_last_speed_value = 0.0
g_last_steering_angle = 0.0

#===============================================================================
#
# REWARD
#
#===============================================================================

def reward_function(params):
  """Reward function is:

  f(s,w,h,t,p) = 1.0 * W(s,Ks) * W(w,Kw) * W(h,Kh) * W(t,Kt) * W(p,Kp) * W(l,Kl)

  s: speed factor, linear 0..1 for range of speed from 0 to MAX_SPEED
  w: wheel factor, non-linear 0..1 for wheels being off the track and
     vehicle in danger of going off the track.  We want to use the full
     width of the track for smoothing curves so we only apply wheel
     factor if the car is hanging off the track.
  h: heading factor, 0..1 for range of angle between car heading vector
     and the track direction vector.  This is the current heading
     based on the immediate direction of the car regardless of steering.
  t: steering factor, 0..1 for steering pressure if steering the wrong
     direction to correct the heading.
  p: progress factor
  l: lane factor

  W: Weighting function: (1.0 - (1.0 - f) * Kf)
  Kx: Weight of respective factor

      Example 1:
        s = 0
        Ks = 0.5
        reward = (1.0 - ((1.0 - s) * Ks)) = 1.0 - (1.0 - 0) * 0.5 = 0.5

      Example 2:
        s = 0.25
        Ks = 1.0
        reward = (1.0 - ((1.0 - s) * Ks)) = 1.0 - (1.0 - 0.25) * 1.0 = 0.25

      Example 2:
        s = 1.0
        Ks = 0.1
        reward = (1.0 - ((1.0 - s) * Ks)) = 1.0 - (1.0 - 1.0) * 1.0 = 1.0

  params:

  from https://docs.aws.amazon.com/deepracer/latest/developerguide/deepracer-reward-function-input.html

    Name                  Type                    Value(s)
    ----                  ----                    --------
    track_width           float                   0..Dtrack (varies)
    distance_from_center  float                   0..~track_width/2
    speed                 float                   0.0..5.0
    steering_angle        float                   -30..30
    all_wheels_on_track   Boolean                 True|False
    heading               float                   -180..+180
    waypoints             list of [float, float]  [[xw,0,yw,0] ... [xw,Max-1, yw,Max-1]]
    closest_waypoints     [int, int]              [0..Max-2, 1..Max-1]
    steps                 int                     0..Nstep
    progress              float                   0..100
    is_left_of_center     Boolean                 True|False
    is_reversed           Boolean                 True|False
    x                     float
    y                     float

  """

  # s: Speed Factor: ideal speed is max
  speed_factor = calculate_speed_factor(params)

  # w: Wheel Factor: apply pressure when wheels are off the track
  wheel_factor = calculate_wheel_factor(params)

  # h: Heading Factor
  heading_factor = calculate_heading_factor(params)

  # t: Steering Factor
  steering_factor = calculate_steering_factor(params)

  # p: Progress Factor: TBD
  progress_factor = calculate_progress_factor(params)

  # l: Lane Factor
  lane_factor = calculate_lane_factor(params)

  # r: Race line factor (distance from)
  race_line_factor = calculate_race_line_factor(params)

  # Log for validation
  if DEBUG_LOG_ENABLED:
    print("s: %0.2f, w: %0.2f, h: %0.2f, t: %0.2f, p: %0.2f, l: %0.2f r: %0.2f" %
          (speed_factor, wheel_factor, heading_factor, steering_factor,
           progress_factor, lane_factor, race_line_factor))

  reward = 1.0
  reward *= apply_weight(speed_factor, SPEED_FACTOR_WEIGHT, SPEED_FACTOR_EASING)
  reward *= apply_weight(wheel_factor, WHEEL_FACTOR_WEIGHT, WHEEL_FACTOR_EASING)
  reward *= apply_weight(heading_factor, HEADING_FACTOR_WEIGHT,
                         HEADING_FACTOR_EASING)
  reward *= apply_weight(steering_factor, STEERING_FACTOR_WEIGHT,
                         STEERING_FACTOR_EASING)
  reward *= apply_weight(progress_factor, PROGRESS_FACTOR_WEIGHT)
  reward *= apply_weight(lane_factor, LANE_FACTOR_WEIGHT, LANE_FACTOR_EASING)
  reward *= apply_weight(race_line_factor, RACE_LINE_FACTOR_WEIGHT, RACE_LINE_FACTOR_EASING)

  return float(max(reward, 1e-3)) # make sure we never return exactly zero



#===============================================================================
#
# RACE LINE
#
#===============================================================================
def calculate_race_line_factor(params):
    # Reward for track position
    current_position = Point(params['x'], params['y'])
    race_line = LineString(RACE_LINE_WAYPOINTS)
    distance = current_position.distance(race_line)
    # clamp reward to range (0..1) mapped to distance (track_width..0).
    # This could be negative since the car center can be off the track but
    # still not disqualified.

    factor = 1.0 - distance / (params['track_width'] / 2.0)
    #print("x %0.2f y %0.2f distance %0.2f track_width %0.2f factor %0.7f" % (params['x'], params['y'], distance, params['track_width'], factor))
    return float(max(factor, 0.0))
  

#===============================================================================
#
# SPEED
#
#===============================================================================

def penalize_downshifting(speed):
  global g_last_speed_value
  if g_last_speed_value > speed:
    speed_factor = 1e-3
  else:
    speed_factor = 1.0
  g_last_speed_value = speed
  return speed_factor
  
def reward_upshifting(speed):
  global g_last_speed_value
  if g_last_speed_value < speed:
    speed_factor = 1.0
  else:
    speed_factor = 0.5
  g_last_speed_value = speed
  return speed_factor

def speed_or_acceleration(speed):
  """ Reward top speed AND any acceleration as well """
  global g_last_speed_value
  if speed > g_last_speed_value:
    speed_factor = 1.0
  else:
    speed_factor = percentage_speed(speed)
  return speed_factor

def percentage_speed(speed):
  return speed / MAX_SPEED

def calculate_speed_factor(params):
  """ Calculate the speed factor """

  # make calls here not affect each other
  speed_factor = percentage_speed(params['speed'])
  return min(speed_factor, 1.0)


#===============================================================================
#
# PROGRESS
#
#===============================================================================

def progress_over_time(progress):
  """ Calculate the progress per time.  Note that
  we rely on how the simulation code calculates
  progress which is an unknown algorithm.

  The nice thing about this algorithm is that is scales
  up rewards exponentially, as the differences in lower
  lap times are more valueable than at higher lap times.
  """
  global g_last_progress_value
  global g_last_progress_time
  current_time = time.time()
  # progress is 0..100
  if g_last_progress_value == 0:
    progress_factor = 1.0 # arbitrary but positive enough to promote going
  else:
    # time can be anything, but probably ~20s/lap, 15fps:
    #       1s/15frames = 67ms/frame = 0.067s
    #
    #   for 30s/lap: 30s*15f/s = 400 frames
    #         => expected progress of 100/400 = 0.25 per frame
    #         => 3.7
    #
    #   assuming 20s/lap: 20s*15f/s = 300 frames
    #         => expected progress of 100/300 = 0.3 progress per frame / 0.067s
    #         => 4.47
    #
    #   for 13s/lap: 13s*15f/s = 195 frames
    #         => expected progress of 100/195 = 0.51 per frame
    #         => 7.6
    #
    #   for 12s/lap: 12s*15f/s = 180 frames
    #         => expected progress of 100/180 = 0.55 per frame
    #         => 8.2
    #
    #   for 10s/lap: 10s*15f/s = 150 frames
    #         => expected progress of 100/150 = 0.67 per frame
    #         => 10
    #
    #   for 9s/lap: 9s*15f/s = 135 frames
    #         => expected progress of 100/135 = 0.74 per frame
    #         => 11.04
    #
    #   for 8s/lap: 8s*15f/s = 120 frames
    #         => expected progress of 100/120 = 0.83 per frame
    #         => 12.39
    #
    progress_factor = (progress - g_last_progress_value) / (current_time - g_last_progress_time)

  g_last_progress_value = progress
  g_last_progress_time = current_time
  return max(progress_factor, 0.0)  #make sure not going backwards

def progress_since_last(progress):
  global g_last_progress_value
  # progress is 0..100. The logic in DR environment code ensures this always
  # increases for the episode, regardless if the car is going backward.
  if g_last_progress_value > progress:
    g_last_progress_value = 0
  progress_factor = (progress - g_last_progress_value) / 100 # divide by 100 to get percentage of track
  g_last_progress_value = progress
  return progress_factor

def calculate_progress_factor(params):
  progress_factor = 1.0
  return min(progress_factor, 1.0)

#===============================================================================
#
# WHEELS
#
#===============================================================================


def all_wheels_must_be_on_track(all_wheels_on_track):
  """ Return low factor if car doesn't have all its wheels on the track """
  if not all_wheels_on_track:
    wheel_factor = 1e-3   # hard code multiplier rather than making it
                          # continuous since we don't know the width of
                          # the car wheelbase
  else:
    wheel_factor = 1.0
  return wheel_factor


def calculate_wheel_factor(params):
  """ Calculate the wheel factor """
  wheel_factor = all_wheels_must_be_on_track(params['all_wheels_on_track'])
  return min(wheel_factor, 1.0)


#===============================================================================
#
# HEADING
#
#===============================================================================

def look_ahead_heading(waypoints, current_waypoint, heading):
  """ Apply pressure based on upcoming track heading """
  
  track_headings = []
  v_init = current_waypoint
  for i in range(3):
    v1 = waypoints[(current_waypoint + 2*i) % len(waypoints)]
    v2 = waypoints[(current_waypoint + 2*i + 1) % len(waypoints)]
    track_heading = angle_of_vector([v1,v2])
    track_headings.append(track_heading)
  print(track_headings)
  return 1.0

def calculate_heading_factor(params):
  """ Calculate the heading factor """
  """
  # SUPRESS: This is too experimental while we haven't finished tracks yet
  closest_waypoints = params['closest_waypoints']
  waypoints = params['waypoints']
  heading = params['heading']

  # Calculate the immediate track angle
  wp1 = waypoints[closest_waypoints[0]]
  wp2 = waypoints[closest_waypoints[1]]
  ta1 = angle_of_vector([wp1,wp2])
  print("track angle 1: %i" % ta1)

  # h: Heading Factor: apply pressure as heading is different than track angle

  # Find closest angle, accounting for possibility of wrapping
  a = abs(ta1 - heading)
  b = abs(ta1 - (heading + 360))
  heading_delta = min(a,b)
  # hard fail if going backwards
  if heading_delta > 90:
    heading_factor = 1e-3
  elif heading_delta > 45:
    heading_factor = 0.5
  else:
    heading_factor = 1.0
  """
  heading_factor = 1.0
  heading_factor = look_ahead_heading(params['waypoints'],
                                      params['closest_waypoints'][0],
                                      params['heading'])
  return min(heading_factor, 1.0)


#===============================================================================
#
# STEERING
#
#===============================================================================

def penalize_steering_change(steering_angle, greater=True, less=True):
  ''' 
  Penalize steering changes 
    
  @greater: penalize sharper turning
  @less: penalize straightening
  '''
  global g_last_steering_angle
  if abs(steering_angle) > g_last_steering_angle and greater:
    # turning sharper
    steering_penalty = 1.0
  elif abs(steering_angle) < g_last_steering_angle and less:
    # straightening
    steering_penalty = 1.0
  else:
    steering_penalty = 0.0
  g_last_steering_angle = abs(steering_angle)
  return 1.0 - steering_penalty

def percentage_steering_angle(steering_angle):
  steering_severity = abs(steering_angle) / MAX_STEERING_ANGLE
  return max(min(1.0 - steering_severity, 1.0), 0.0)

def calculate_steering_factor(params):
  """ Calculate the steering factor """
  steering_factor = percentage_steering_angle(params['steering_angle'])
  return min(steering_factor, 1.0)


#===============================================================================
#
# LANE
#
#===============================================================================


def percentage_distance_from_track_center(track_width, distance_from_center):
  """ Return a linear percentage distance along the track width from
  the center to the outside
  """
  # make sure not negative, in case distance_from_center is over the track_width
  distance = distance_from_center / (track_width/2.0)
  return max(min(1.0 - distance, 1.0), 0.0)

def penalize_off_track(track_width, distance_from_center):
  if distance_from_center >= (track_width/2.0):
    penalty = 1.0
  else:
    penalty = 0.0
  return (1.0 - penalty)

def calculate_lane_factor(params):
  """ Calulcate the reward for the position on the track.
  Be careful to account for the wheel factor here, possibly merge
  the two later.
  """
  lane_factor = percentage_distance_from_track_center(params['track_width'],
                                   params['distance_from_center'])
  return min(lane_factor, 1.0)


#===============================================================================
#
# HELPER METHODS
#
#===============================================================================

def apply_weight(factor, weight, easing='linear'):
  """Apply a weight to factor, clamping both arguments at 1.0

  Factor values will be 0..1. This function will cause the range of the
  factor values to be reduced according to:

    f = 1 - weight * (1 - factor)^easing

  In simple terms, a weight of 0.5 will cause the factor to only have weighted
  values of 0.5..1.0. If we further apply an easing, the decay from 1.0 toward
  the weighted minimum will be along a curve.
  """

  f_clamp = min(factor, 1.0)
  w_clamp = min(weight, 1.0)
  if EASING_FUNCTIONS[easing]:
    ease = EASING_FUNCTIONS[easing]
  else:
    ease = EASING_FUNCTIONS['linear']

  return 1.0 - w_clamp * ease(1.0 - f_clamp)


def vector_of_angle(angle):
  """ Unit vector of an angle in degrees. """
  return [[0.0, 0.0], [math.sin(math.radians(angle)), math.cos(math.radians(angle))]]


def angle_of_vector(vector):
  """ Calculate the angle of the vector in degrees relative to
  a normal 2d coordinate system.  This is useful for finding the
  angle between two waypoints.

    vector: [[x0,y0],[x1,y1]]

  """
  rad = math.atan2(vector[1][1] - vector[0][1], vector[1][0] - vector[0][0])
  return math.degrees(rad)

#
# SCALING FUNCTIONS
#

def ease_linear(x):
  return x

def ease_quadratic(x):
  return x*x

def ease_cubic(x):
  return abs(x*x*x)

def ease_quartic(x):
  return x*x*x*x

def ease_quintic(x):
  return abs(x*x*x*x*x)

def ease_septic(x):
  return abs(x*x*x*x*x*x*x)

def ease_nonic(x):
  return abs(x*x*x*x*x*x*x*x*x)

EASING_FUNCTIONS = {
    'linear': ease_linear,
    'quadratic': ease_quadratic,
    'cubic': ease_cubic,
    'quartic': ease_quartic,
    'quintic': ease_quintic,
    'septic': ease_septic,
    'nonic': ease_nonic
}


