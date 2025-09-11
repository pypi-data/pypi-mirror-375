import numpy as np

def quat2ang(q):
  return (quat2roll(q), quat2pitch(q), quat2yaw(q))

def quat2ang_vec(Q):
  h = np.asarray(Q.shape)
  if h[0] == 4:
    N = h[1]
    r = np.zeros((1,N))
    p = np.zeros((1,N))
    y = np.zeros((1,N))
  elif h[1] == 4:
    N = h[0]
    r = np.zeros((N,1))
    p = np.zeros((N,1))
    y = np.zeros((N,1))

  for ind,q in enumerate(Q):
    r[ind],p[ind],y[ind] = quat2ang(q)

  return (np.squeeze(r),np.squeeze(p),np.squeeze(y))


def ang2quat(roll,pitch,yaw):
  # 3-2-1 rotation
  return qprod([np.cos(yaw/2),0,0,np.sin(yaw/2)],qprod([np.cos(pitch/2),0,np.sin(pitch/2),0], [np.cos(roll/2),np.sin(roll/2),0,0]))

def ang2quat_vec(roll,pitch,yaw):
  Q = np.zeros((len(roll),4))
  for ind,(r,p,y) in enumerate(zip(roll,pitch,yaw)):
    Q[ind] = ang2quat(r,p,y)
  return Q


def quat2rmat(qin):
    q = qconj(qin)
    rmat = np.zeros((3,3))
    rmat[0,0] = q[0]**2 + q[1]**2 - q[2]**2 - q[3]**2
    rmat[0,1] = 2*(q[1]*q[2] + q[0]*q[3])
    rmat[0,2] = 2*(q[1]*q[3] - q[0]*q[2])
    rmat[1,0] = 2*(q[1]*q[2] - q[0]*q[3])
    rmat[1,1] = q[0]**2 - q[1]**2 + q[2]**2 - q[3]**2
    rmat[1,2] = 2*(q[2]*q[3] + q[0]*q[1])
    rmat[2,0] = 2*(q[1]*q[3] + q[0]*q[2])
    rmat[2,1] = 2*(q[2]*q[3] - q[0]*q[1])
    rmat[2,2] = q[0]**2 - q[1]**2 - q[2]**2 + q[3]**2
    return rmat

def quat2roll(V):
	return np.arctan2( 2*(V[2]*V[3] + V[0]*V[1]), V[0]*V[0] - V[1]*V[1] - V[2]*V[2] + V[3]*V[3] )

def quat2pitch(V):
	return np.arcsin( 2*(V[0]*V[2] - V[1]*V[3]) )

def quat2yaw(V):
	return np.arctan2( 2*(V[1]*V[2] + V[0]*V[3]), V[0]*V[0] + V[1]*V[1] - V[2]*V[2] - V[3]*V[3] )

def qnorm(q):
  q2 = np.copy(q)
  return q2/np.linalg.norm(q2)

def qmin(q):
  qout = np.copy(q)
  if qout[0] < 0:
    qout[0] = -qout[0]
    qout[1] = -qout[1]
    qout[2] = -qout[2]
    qout[3] = -qout[3]
  return qout

def qconj(q):
  qout = 0*q
  qout[0] = q[0]
  qout[1] = -q[1]
  qout[2] = -q[2]
  qout[3] = -q[3]
  return qout

def qrot(q,v):
  vp = np.copy(v)
  # a = cross(q.xyz, v)
  tv_1 = q[2]*v[2] - q[3]*v[1] + q[0]*v[0]
  tv_2 = q[3]*v[0] - q[1]*v[2] + q[0]*v[1]
  tv_3 = q[1]*v[1] - q[2]*v[0] + q[0]*v[2]
  
  # v' = cross(q.xyz, a)
  vp[0] = q[2]*tv_3 - q[3]*tv_2
  vp[1] = q[3]*tv_1 - q[1]*tv_3
  vp[2] = q[1]*tv_2 - q[2]*tv_1
  
  # v' = 2*v' + v;
  return 2*vp + v

def qrot_vec(Q,V):
  if Q.ndim == 2:
    Vp = 0*V
    for idx,(v,q) in enumerate(zip(V,Q)):
      Vp[idx] = qrot(q,v)
    return Vp
  else:
    return qrot(Q,V)

def qprod(q,r):
  qr = np.copy(q)
  qr[0] = q[0]*r[0] - q[1]*r[1] - q[2]*r[2] - q[3]*r[3]
  qr[1] = q[0]*r[1] + q[1]*r[0] + q[2]*r[3] - q[3]*r[2]
  qr[2] = q[0]*r[2] - q[1]*r[3] + q[2]*r[0] + q[3]*r[1]
  qr[3] = q[0]*r[3] + q[1]*r[2] - q[2]*r[1] + q[3]*r[0]
  return qr

def gyr_int(dt, gyr, q0):
  qdot = 0.5 * qprod(q0,np.array([0,gyr[0],gyr[1],gyr[2]]))
  q = q0 + qdot*dt
  q = qnorm(q)
  q = qmin(q)
  return q

def gyr_int_vec(t, gyr, q0):
  q = np.zeros((len(t),4))
  for idx,(ti,g) in enumerate(zip(t,gyr)):
    if idx == 0:
      q[idx] = q0
      tlast = ti
    else:
      dt = ti-tlast
      q[idx] = gyr_int(dt,g,q[idx-1])
      tlast = ti

  return q

def mag_correct_q(M_m,q,mag_dec=0):
  roll = quat2roll(q)
  pitch = quat2pitch(q)
  q_rp = ang2quat(roll,pitch,0)
  return qprod(mag2q(M_m,q_rp,mag_dec),q_rp)

def mag_correct_q_vec(M_m,Q,mag_dec=0):
  Qout = 0*Q
  for idx,(q,mm) in enumerate(zip(Q,M_m)):
    Qout[idx] = mag_correct_q(mm,q,mag_dec=mag_dec)
  return Qout

def mag2q(M_m,q,mag_dec=0):

  roll = quat2roll(q)
  pitch = quat2pitch(q)
  mm_x = M_m[0]*np.cos(pitch) + M_m[2]*np.sin(pitch)
  mm_y = M_m[0]*np.sin(roll)*np.sin(pitch) + M_m[1]*np.cos(roll) - M_m[2]*np.sin(roll)*np.cos(pitch)

  yaw = np.arctan2(-mm_y, mm_x)
  return qprod([np.cos(yaw/2),0,0,np.sin(yaw/2)], [np.cos(mag_dec/2),0,0,np.sin(mag_dec/2)])

def mag2yaw(M_m,q,mag_dec=0):
  return quat2yaw(mag2q(M_m,q,mag_dec))

def acc2q_vec(A):
  Q = np.zeros((np.shape(A)[0],4))
  for idx,a in enumerate(A):
    Q[idx] = acc2q(a)

  return Q

def acc2q(a):
  q = np.array([1.0, 0.0, 0.0, 0.0])
  Axy = np.sqrt(a[0]**2 + a[1]**2)
  if Axy > 0:
    temp = 0.5*np.arctan2(Axy, a[2])
    q[0] = np.cos(temp)
    q[1] = np.sin(temp) * a[1] / Axy
    q[2] =-np.sin(temp) * a[0] / Axy

  return q

def acc2rpy(a):
  return quat2ang(acc2q(a))

def accmag2q_vec(A,M,mag_dec=0):
  Q = np.zeros((np.shape(A)[0],4))
  for idx,(a,m) in enumerate(zip(A,M)):
    qacc = acc2q(a)
    qmag = mag2q(m,qacc,mag_dec)
    Q[idx] = qprod(qmag,qacc)
  return Q

def accmag2q(A,M,mag_dec=0):
  qacc = acc2q(A)
  qmag = mag2q(M,qacc,mag_dec)
  return qprod(qmag,qacc)

def accmag2rpy(A,M,mag_dec=0):
  return quat2ang(accmag2q(A,M,mag_dec))

def quat_rponly(Q):
  Qout = 0*Q
  for idx,(q) in enumerate(Q):
    r,p,y = quat2ang(q)
    Qout[idx] = ang2quat(r,p,0*y)

  return Qout

def yaw_diff(a0,a1):
  q0 = qconj(ang2quat(0,0,a0))
  q1 = ang2quat(0,0,a1)
  return quat2yaw(qprod(q0,q1))
