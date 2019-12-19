"""
AWS DeepRacer reward function
"""
import bisect
import math
from numpy import array
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import LinearRing, LineString
import time

CANADA_TRACK_RACE_LINE = \
array([[ 4.60499992,  1.63285708],
       [ 4.50177863,  1.66231022],
       [ 4.397405  ,  1.69133908],
       [ 4.29329237,  1.72099132],
       [ 4.18944225,  1.75127247],
       [ 4.08585587,  1.78218576],
       [ 3.98253407,  1.81373295],
       [ 3.87947695,  1.84591389],
       [ 3.77668368,  1.87872605],
       [ 3.67415201,  1.91216348],
       [ 3.5718788 ,  1.94621808],
       [ 3.46985985,  1.98087917],
       [ 3.36808957,  2.01613283],
       [ 3.26656173,  2.0519636 ],
       [ 3.16526981,  2.08835527],
       [ 3.06420673,  2.12529044],
       [ 2.96336495,  2.16275051],
       [ 2.86273727,  2.20071781],
       [ 2.76231689,  2.23917545],
       [ 2.66209706,  2.27810665],
       [ 2.56519546,  2.31455827],
       [ 2.46868767,  2.34845144],
       [ 2.37272721,  2.3786251 ],
       [ 2.27748714,  2.40408579],
       [ 2.1831951 ,  2.4240024 ],
       [ 2.09014361,  2.43771542],
       [ 1.99868135,  2.44474411],
       [ 1.90920634,  2.4447451 ],
       [ 1.82213954,  2.43753482],
       [ 1.73792309,  2.42302998],
       [ 1.65699883,  2.40125957],
       [ 1.57981361,  2.37231784],
       [ 1.50681532,  2.33635597],
       [ 1.43845633,  2.29356682],
       [ 1.37517021,  2.24420829],
       [ 1.31741062,  2.18854684],
       [ 1.26562165,  2.12689622],
       [ 1.22023987,  2.05960988],
       [ 1.18170778,  1.98707034],
       [ 1.15045957,  1.90970447],
       [ 1.12690676,  1.82799235],
       [ 1.11142146,  1.74247295],
       [ 1.10430596,  1.65374989],
       [ 1.10578686,  1.56248211],
       [ 1.11596491,  1.46938361],
       [ 1.13476934,  1.37520343],
       [ 1.16194416,  1.28068793],
       [ 1.19703329,  1.18653614],
       [ 1.23936236,  1.09334208],
       [ 1.28808655,  1.0015392 ],
       [ 1.34221521,  0.91135283],
       [ 1.40068473,  0.82278617],
       [ 1.46241973,  0.73564229],
       [ 1.5263488 ,  0.64955884],
       [ 1.59141301,  0.56405822],
       [ 1.65495283,  0.48034491],
       [ 1.7182262 ,  0.3964979 ],
       [ 1.78104486,  0.31242197],
       [ 1.84325473,  0.22803801],
       [ 1.90473478,  0.14328226],
       [ 1.96539429,  0.05810505],
       [ 2.02517569, -0.02752747],
       [ 2.08404926, -0.11363556],
       [ 2.14201613, -0.20022371],
       [ 2.19910498, -0.28728172],
       [ 2.25536859, -0.37478583],
       [ 2.31088468, -0.46269779],
       [ 2.36575054, -0.55096743],
       [ 2.42007947, -0.63953443],
       [ 2.47399437, -0.72833196],
       [ 2.52762131, -0.81729047],
       [ 2.58155385, -0.90713366],
       [ 2.63632485, -0.99652478],
       [ 2.69247642, -1.0850014 ],
       [ 2.75044334, -1.17202242],
       [ 2.81056695, -1.25703678],
       [ 2.87311394, -1.3395243 ],
       [ 2.93828241, -1.41900302],
       [ 3.00618819, -1.49504315],
       [ 3.07687232, -1.5672635 ],
       [ 3.15030956, -1.63533356],
       [ 3.22640766, -1.69899761],
       [ 3.3050362 , -1.75805337],
       [ 3.38602816, -1.81237144],
       [ 3.46919448, -1.86189174],
       [ 3.55433167, -1.90663037],
       [ 3.64123723, -1.94666328],
       [ 3.72971298, -1.98213439],
       [ 3.81957388, -2.0132468 ],
       [ 3.91065232, -2.04026087],
       [ 4.00280125, -2.06348863],
       [ 4.09589444, -2.08328553],
       [ 4.18982118, -2.10004797],
       [ 4.2844831 , -2.11419057],
       [ 4.37978279, -2.12614824],
       [ 4.47561355, -2.13637496],
       [ 4.57185564, -2.14532899],
       [ 4.66837174, -2.15347415],
       [ 4.76967735, -2.16164275],
       [ 4.87099313, -2.17029977],
       [ 4.97232136, -2.17958857],
       [ 5.07366368, -2.18964571],
       [ 5.17502089, -2.20059631],
       [ 5.27639275, -2.21254901],
       [ 5.37777778, -2.22558966],
       [ 5.47917322, -2.23978602],
       [ 5.58057496, -2.25517769],
       [ 5.68197766, -2.27178292],
       [ 5.7833748 , -2.28959595],
       [ 5.88475903, -2.308588  ],
       [ 5.98612244, -2.32871055],
       [ 6.087457  , -2.34989805],
       [ 6.18875494, -2.37207264],
       [ 6.29000916, -2.39514656],
       [ 6.39121372, -2.41902434],
       [ 6.49236389, -2.44360931],
       [ 6.59345649, -2.46880287],
       [ 6.69448953, -2.4945088 ],
       [ 6.79520895, -2.52056492],
       [ 6.89596575, -2.54598416],
       [ 6.99680557, -2.57019992],
       [ 7.09776631, -2.59265372],
       [ 7.19885953, -2.61279225],
       [ 7.30006398, -2.63007177],
       [ 7.40132592, -2.64395223],
       [ 7.50255912, -2.65392315],
       [ 7.60364403, -2.659479  ],
       [ 7.70442509, -2.6601389 ],
       [ 7.80470529, -2.65542973],
       [ 7.90424129, -2.64490293],
       [ 8.00273632, -2.62813221],
       [ 8.09982474, -2.60468972],
       [ 8.19506502, -2.57418691],
       [ 8.28791616, -2.53625916],
       [ 8.37771308, -2.49059528],
       [ 8.46364177, -2.43699168],
       [ 8.54471429, -2.375413  ],
       [ 8.61978432, -2.30608825],
       [ 8.6876185 , -2.22958448],
       [ 8.74701941, -2.1468211 ],
       [ 8.79700837, -2.05902878],
       [ 8.83690456, -1.96760123],
       [ 8.86637086, -1.8739665 ],
       [ 8.88539635, -1.77947308],
       [ 8.8942435 , -1.68531061],
       [ 8.89334089, -1.59247495],
       [ 8.88322321, -1.5017682 ],
       [ 8.86448766, -1.41380961],
       [ 8.83772562, -1.32906887],
       [ 8.80354053, -1.24787486],
       [ 8.76249361, -1.17045516],
       [ 8.71512384, -1.09694345],
       [ 8.66193959, -1.02739737],
       [ 8.60341951, -0.9618106 ],
       [ 8.54005059, -0.90009221],
       [ 8.47230613, -0.84208868],
       [ 8.40068011, -0.78756018],
       [ 8.32567637, -0.73619357],
       [ 8.24782408, -0.68759342],
       [ 8.16768271, -0.64128252],
       [ 8.08583863, -0.59671272],
       [ 8.00289476, -0.55328509],
       [ 7.91342758, -0.50556483],
       [ 7.82460166, -0.4569035 ],
       [ 7.73658156, -0.40706595],
       [ 7.64951332, -0.35584813],
       [ 7.56351824, -0.30308605],
       [ 7.47870116, -0.24864355],
       [ 7.39514592, -0.19241847],
       [ 7.31292336, -0.13433059],
       [ 7.23208873, -0.07432491],
       [ 7.15268962, -0.01236   ],
       [ 7.07476654,  0.05159287],
       [ 6.99835531,  0.11755316],
       [ 6.92348765,  0.18553177],
       [ 6.8501971 ,  0.2555384 ],
       [ 6.77851997,  0.32758133],
       [ 6.70850125,  0.40165599],
       [ 6.6406844 ,  0.47719206],
       [ 6.57129934,  0.55059828],
       [ 6.50039736,  0.62177192],
       [ 6.42803914,  0.69061121],
       [ 6.35428818,  0.75702883],
       [ 6.27921038,  0.82095967],
       [ 6.20287123,  0.88236724],
       [ 6.1253276 ,  0.94123871],
       [ 6.0466227 ,  0.9975836 ],
       [ 5.96678495,  1.05143902],
       [ 5.88582435,  1.10286681],
       [ 5.80372864,  1.15194702],
       [ 5.72046715,  1.19878346],
       [ 5.63598525,  1.24348788],
       [ 5.55021144,  1.28618621],
       [ 5.46306298,  1.3270161 ],
       [ 5.37444651,  1.36611639],
       [ 5.28426661,  1.40362736],
       [ 5.19243126,  1.43968617],
       [ 5.09886482,  1.47442854],
       [ 5.00351973,  1.50798708],
       [ 4.90638731,  1.54048936],
       [ 4.80750834,  1.57205698],
       [ 4.70698886,  1.60280861],
       [ 4.60499992,  1.63285708]])

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
        array([[ 6.30537067,  2.67802454],
       [ 6.19447935,  2.68004422],
       [ 6.08297515,  2.67857232],
       [ 5.97103875,  2.6739853 ],
       [ 5.85882446,  2.6666801 ],
       [ 5.74645759,  2.65707069],
       [ 5.63514905,  2.64570431],
       [ 5.52399576,  2.63600622],
       [ 5.41299534,  2.62793119],
       [ 5.30215148,  2.62143487],
       [ 5.19147178,  2.6164718 ],
       [ 5.08096678,  2.61299524],
       [ 4.97064918,  2.6109554 ],
       [ 4.86053321,  2.61029781],
       [ 4.75063427,  2.6109636 ],
       [ 4.64096849,  2.61288768],
       [ 4.53155264,  2.6159994 ],
       [ 4.42240395,  2.62022105],
       [ 4.3135407 ,  2.62546992],
       [ 4.20498178,  2.63165703],
       [ 4.09674613,  2.63868861],
       [ 3.98885061,  2.64646675],
       [ 3.88130693,  2.65489125],
       [ 3.77411732,  2.66386117],
       [ 3.66727035,  2.67327709],
       [ 3.56073657,  2.68304209],
       [ 3.45569922,  2.6923941 ],
       [ 3.349598  ,  2.70077449],
       [ 3.24079481,  2.70743938],
       [ 3.12650965,  2.71145929],
       [ 3.00453354,  2.71140423],
       [ 2.87945576,  2.70562975],
       [ 2.75695361,  2.69328826],
       [ 2.63918623,  2.67409935],
       [ 2.52648201,  2.64788765],
       [ 2.41885347,  2.61447933],
       [ 2.31645389,  2.57373296],
       [ 2.21964065,  2.52558026],
       [ 2.1289364 ,  2.47007263],
       [ 2.04498736,  2.40740032],
       [ 1.9685052 ,  2.33791711],
       [ 1.90022057,  2.26214033],
       [ 1.84082557,  2.18074997],
       [ 1.79093556,  2.09456514],
       [ 1.75103985,  2.00452109],
       [ 1.7214891 ,  1.91162652],
       [ 1.70248934,  1.8169266 ],
       [ 1.69408969,  1.7214698 ],
       [ 1.69620235,  1.62627464],
       [ 1.70861658,  1.53230593],
       [ 1.73102239,  1.4404585 ],
       [ 1.76302383,  1.35154516],
       [ 1.80415825,  1.26628928],
       [ 1.85392007,  1.18532528],
       [ 1.91176391,  1.10919294],
       [ 1.97712148,  1.03833913],
       [ 2.04940615,  0.97311389],
       [ 2.12802031,  0.91376754],
       [ 2.21236478,  0.86045048],
       [ 2.30183982,  0.81320471],
       [ 2.39584815,  0.77195461],
       [ 2.49380167,  0.7365021 ],
       [ 2.59512537,  0.70651976],
       [ 2.69926279,  0.68155118],
       [ 2.80567455,  0.66101039],
       [ 2.91383545,  0.64419622],
       [ 3.02322865,  0.6303059 ],
       [ 3.13336308,  0.61844663],
       [ 3.24383257,  0.60767413],
       [ 3.35386808,  0.59683058],
       [ 3.46364061,  0.58526984],
       [ 3.57291128,  0.57234289],
       [ 3.6814523 ,  0.55743604],
       [ 3.78904938,  0.53998067],
       [ 3.8954999 ,  0.51945395],
       [ 4.00060786,  0.49537939],
       [ 4.10417187,  0.46733099],
       [ 4.20595709,  0.43493452],
       [ 4.3056626 ,  0.39789245],
       [ 4.40289833,  0.35601691],
       [ 4.49719048,  0.30924928],
       [ 4.58803434,  0.25767525],
       [ 4.67496443,  0.20150648],
       [ 4.75761364,  0.14104288],
       [ 4.83573842,  0.07662647],
       [ 4.90922093,  0.00860861],
       [ 4.97804554, -0.06267717],
       [ 5.04227129, -0.13692825],
       [ 5.10200402, -0.21387877],
       [ 5.15737227, -0.2933008 ],
       [ 5.20850901, -0.37500256],
       [ 5.25553999, -0.45882473],
       [ 5.29857688, -0.54463615],
       [ 5.3377125 , -0.63232992],
       [ 5.37366743, -0.72152117],
       [ 5.40676511, -0.812034  ],
       [ 5.43733142, -0.90370038],
       [ 5.46569746, -0.99635677],
       [ 5.49220084, -1.08984208],
       [ 5.51718703, -1.18399598],
       [ 5.54059031, -1.27696552],
       [ 5.56515394, -1.36906804],
       [ 5.59187632, -1.45953807],
       [ 5.62165928, -1.54764737],
       [ 5.65528528, -1.63270804],
       [ 5.69341037, -1.71406563],
       [ 5.73657241, -1.79107997],
       [ 5.78520696, -1.8630957 ],
       [ 5.83966164, -1.92940422],
       [ 5.90040744, -1.98895169],
       [ 5.96688453, -2.04166439],
       [ 6.0386328 , -2.08740474],
       [ 6.11525433, -2.12597381],
       [ 6.1963916 , -2.15710097],
       [ 6.28169746, -2.18044996],
       [ 6.37081072, -2.1956184 ],
       [ 6.46332836, -2.20213836],
       [ 6.55876618, -2.19949531],
       [ 6.65651277, -2.18715053],
       [ 6.75576344, -2.16459862],
       [ 6.85543564, -2.13148313],
       [ 6.95408639, -2.08776595],
       [ 7.04990928, -2.03395358],
       [ 7.14099351, -1.97121871],
       [ 7.22585953, -1.90113714],
       [ 7.30380653, -1.82521495],
       [ 7.37478834, -1.7446278 ],
       [ 7.43910821, -1.66022548],
       [ 7.4972059 , -1.57262998],
       [ 7.54955206, -1.48231463],
       [ 7.59661705, -1.38965733],
       [ 7.63886292, -1.2949703 ],
       [ 7.6767404 , -1.19851653],
       [ 7.71069661, -1.100523  ],
       [ 7.74118114, -1.0011897 ],
       [ 7.76864636, -0.90069592],
       [ 7.79355241, -0.79920932],
       [ 7.81636799, -0.69689476],
       [ 7.83757032, -0.59392328],
       [ 7.85764454, -0.49047888],
       [ 7.87708212, -0.38676114],
       [ 7.89678644, -0.28077142],
       [ 7.91659758, -0.17479692],
       [ 7.93647836, -0.06883233],
       [ 7.9564603 ,  0.03711785],
       [ 7.97654434,  0.14305349],
       [ 7.99643517,  0.24855836],
       [ 8.01541523,  0.35300831],
       [ 8.03294153,  0.45660377],
       [ 8.04849716,  0.55953094],
       [ 8.06158142,  0.66189217],
       [ 8.07171823,  0.76371816],
       [ 8.07846152,  0.86498796],
       [ 8.08140071,  0.96564625],
       [ 8.08016563,  1.06561445],
       [ 8.074419  ,  1.16479414],
       [ 8.06385874,  1.26306793],
       [ 8.04821275,  1.36029636],
       [ 8.02723657,  1.45631326],
       [ 8.00071483,  1.55092056],
       [ 7.96845723,  1.64388062],
       [ 7.93031377,  1.73491327],
       [ 7.88618067,  1.82369204],
       [ 7.83601077,  1.90984407],
       [ 7.77982983,  1.99295771],
       [ 7.71774543,  2.0725948 ],
       [ 7.64995091,  2.14830912],
       [ 7.57672953,  2.2196764 ],
       [ 7.4984343 ,  2.28631531],
       [ 7.41546909,  2.34791088],
       [ 7.32826621,  2.40423287],
       [ 7.2372574 ,  2.45513633],
       [ 7.14285647,  2.50055976],
       [ 7.04544547,  2.54051107],
       [ 6.94537306,  2.575058  ],
       [ 6.84295739,  2.6043183 ],
       [ 6.73849027,  2.62844831],
       [ 6.63224524,  2.64764207],
       [ 6.52448087,  2.66212497],
       [ 6.4154436 ,  2.67215287],
       [ 6.30537067,  2.67802454]])

# Constants
DEBUG_LOG_ENABLED = True

# Action space constants
MAX_SPEED = 10
MAX_STEERING_ANGLE = 25.0

# As an arbitrary goal, without knowing lengths of
# tracks beforehand, let's try to get 1.0 to be
# the target reward for each step.  An 8s lap on
# any track would be 
#    progress 100 => 8s * 15fps = 120 steps
#    progress 100 => 5s * 15fps = 75 steps
#    progress 100 => 6.67s * 15fps = 100 steps
# 
# The reward gets clamped at 1.0 so too low
# and visualizations get screwy in analysis, but
# too high means the car won't get feedback.
TARGET_NUMBER_STEPS = 100

# Raceline track
RACE_LINE_WAYPOINTS = CANADA_TRACK_RACE_LINE

# TUNING: Adjust these to find tune factors affect on reward
#
# Reward weights, always 0..1.  These are relative to one another
SPEED_FACTOR_WEIGHT = 0.0
SPEED_FACTOR_EASING = 'linear'
WHEEL_FACTOR_WEIGHT = 0.0
WHEEL_FACTOR_EASING = 'linear'
HEADING_FACTOR_WEIGHT = 0.0
HEADING_FACTOR_EASING = 'linear'
STEERING_FACTOR_WEIGHT = 0.5
STEERING_FACTOR_EASING = 'linear'
PROGRESS_FACTOR_WEIGHT = 1.0
PROGRESS_FACTOR_EASING = 'linear'
LANE_FACTOR_WEIGHT = 0.0
LANE_FACTOR_EASING = 'quintic'
RACE_LINE_FACTOR_WEIGHT = 0.0
RACE_LINE_FACTOR_EASING = 'linear'

# Globals
g_last_progress_value = 0.0
g_last_progress_time = 0.0
g_last_speed_value = 0.0
g_last_steering_angle = 0.0
# for getting current race line waypoint distances
g_race_line_dists = [LineString(RACE_LINE_WAYPOINTS).project(Point(p), normalized=True) for p in LineString(RACE_LINE_WAYPOINTS).coords[:-1]] + [1.0]

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

    factor = 1.0 - distance / (params['track_width'] / 3.0)
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

def progress_target(progress):
  global g_last_progress_value
  # delta is percentage of track covered
  delta = progress_since_last(progress)
  progress_target_per_step = 1 / TARGET_NUMBER_STEPS # use 1 instead of 100 to match progress_since_last magnitude
  progress_factor = delta / progress_target_per_step
  return progress_factor

def calculate_progress_factor(params):
  progress_factor = progress_target(params['progress'])
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

def race_line_heading(params):
  current_position = Point(params['x'], params['y'])
  race_line = LineString(RACE_LINE_WAYPOINTS)
  current_ndist = race_line.project(current_position, normalized=True)
  if params['is_reversed']:
    next_index = bisect.bisect_left(g_race_line_dists, current_ndist) - 1
    prev_index = next_index + 1
    if next_index == -1: next_index = len(g_race_line_dists) - 1
  else:
    next_index = bisect.bisect_right(g_race_line_dists, current_ndist)
    prev_index = next_index - 1
    if next_index == len(g_race_line_dists): next_index = 0
  prev_index, next_index
  # Target heading in euler reference coordinates
  #print("nearest race line [%d,%d] at (%0.2f,%0.2f),(%0.2f,%0.2f)" % (prev_index, next_index, RACE_LINE_WAYPOINTS[prev_index][0], RACE_LINE_WAYPOINTS[prev_index][1], RACE_LINE_WAYPOINTS[next_index][0], RACE_LINE_WAYPOINTS[next_index][1]))
  target_heading = angle_of_vector((RACE_LINE_WAYPOINTS[prev_index], RACE_LINE_WAYPOINTS[next_index]))

  #heading_with_steering = params['heading'] + params['steering_angle']
  #if heading_with_steering > 180: heading_with_steering -= 360
  #if heading_with_steering < -180: heading_with_steering += 360

  heading_delta = abs(target_heading - params['heading'])
  if heading_delta > 180: heading_delta = abs(heading_delta - 360)
  #print("heading %0.2f target_heading %0.2f delta %0.2f" % (params['heading'], target_heading, heading_delta))

  heading_factor = 1.0 - heading_delta / 90.0
  #print("heading_factor = %0.2f" % heading_factor)
  return max(heading_factor, 0.0)

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
  heading_factor = race_line_heading(params)
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
  #print("angle_of_vector %0.2f radians, %0.2f degrees" % (rad, math.degrees(rad)))
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


