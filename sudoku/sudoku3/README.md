
          A    B    C    D
        #====+====#====+====#
      a # 1  |    #  2 |  2 #
        #    | 34 #  4 | 3  #
        #----+----#----+----#
      b #    |  2 # 1  | 1  #
        # 34 |    #  4 | 3  #
        #====+====#====+====#
      c #  2 | 1  #    | 12 #
        #  4 |  4 # 3  |    #
        #----+----#----+----#
      d #  2 | 1  # 12 |    #
        # 3  | 3  #    |  4 #
        #====+====#====+====#

Aa = 1      [A, a, ABab].[1]
Ba = 3,4    [B, a, ABab].[3, 4]
Ca = 2,4    [C, a, CDab].[2, 4]
Da = 2,3    [D, a, CDab].[2, 3]
Ab = 3,4
Bb = 2
Cb = 1,4
Db = 1,3
Ac = 2,4
Bc = 1,4
Cc = 3
Dc = 1,2
Ad = 2,3
Bd = 1,3
Cd = 1,2
Dd = 4

A.1 = Aa
A.2 = Ac, Ad
A.3 = Ab, Ad
A.4 = Ab, Ac

B.1 = Bc, Bd
B.2 = Bb
B.3 = Ba, Bd
B.4 = Ba, Bc

C.1 = Cb, Cd
C.2 = Ca, Cd
C.3 = Cc
C.4 = Ca, Cb

D.1 = Db, Dc
D.2 = Da, Dc
D.3 = Da, Db
D.4 = Dd

a.1 = Aa
a.2 = Ca, Da
a.3 = Ba, Da
a.4 = Ba, Ca

b.1 = Cb, Db
b.2 = Bb
b.3 = Ab, Db
b.4 = Ab, Cb

c.1 = Bc, Dc
c.2 = Ac, Dc
c.3 = Cc
c.4 = Ac, Bc

d.1 = Bd, Cd
d.2 = Ad, Cd
d.3 = Ad, Bd
d.4 = Dd

ABab.1 = Aa
ABab.2 = Bb
ABab.3 = [Ba, Ab]
ABab.4 = [Ba, Ab]

CDab.1 = [Cb, Db]
CDab.2 = [Ca, Da]
CDab.3 = [Da, Db]
CDab.4 = [Ca, Cb]

ABcd.1 = [Bc, Bd]
ABcd.2 = [Ac, Ad]
ABcd.3 = [Ad, Bd]
ABcd.4 = [Ac, Bc]

CDcd.1 = [Dc, Cd]
CDcd.2 = [Dc, Cd]
CDcd.3 = Cc
CDcd.4 = Dd


squares = [
    Aa, Ba, Ca, Da,
    Ab, Bb, Cb, Db,
    Ac, Bc, Cc, Dc,
    Ad, Bd, Cd, Dd
]

row_sets = {
    a: [Aa, Ba, Ca, Da],
    b: [Ab, Bb, Cb, Db],
    c: [Ac, Bc, Cc, Dc],
    d: [Ad, Bd, Cd, Dd]
}

col_sets = {
    A: [Aa, Ab, Ac, Ad],
    B: [Ba, Bb, Bc, Bd],
    C: [Ca, Cb, Cc, Cd],
    D: [Da, Db, Dc, Dd]
}

sector_sets = {
    ABab: [Aa, Ba, Ab, Bb],
    CDab: [Ca, Da, Cb, Db],
    ABcd: [Ac, Bc, Ad, Bd],
    CDcd: [Cc, Dc, Cd, Dd]
}

all_sets = row_sets + col_sets + sector_sets
