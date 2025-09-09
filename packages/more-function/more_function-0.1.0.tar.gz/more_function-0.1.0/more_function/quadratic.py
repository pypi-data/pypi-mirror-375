import math

def solve_quadratic(a,b,c):
    '''
    Giải phương trình bậc 2: ax^2+bx+c=0
    a,b,c : float
    -----
    result
    nghiệm làm tròn 2 chữ số của phương trình bậc 2
    '''
    if a==0:
        if b==0:
            return "Phương trình này vô số nghiệm"
        else:
            return [round(-c/b,2)]
    else:
        d=b**2-4*a*c
        if d<0:
            return []
        elif d==0:
            return [round(-b/(2*a),2)]
        else:
            sqt=math.sqrt(d)
            x1=round((-b+sqt)/2*a,2)
            x2=round((-b-sqt)/2*a,2)
            return [x1,x2]

