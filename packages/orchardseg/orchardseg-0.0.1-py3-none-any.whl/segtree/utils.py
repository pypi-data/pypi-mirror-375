import os
from skimage.io import imread

import matplotlib.pyplot as plt
import numpy as np
import cv2 
from tqdm import tqdm 
from skimage.measure import label
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import LocalOutlierFactor
from transformers import pipeline
from scipy.signal import find_peaks
from collections import Counter
import os.path

# CONF = config.get_conf_dict()
homedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# base_dir = CONF['general']['base_directory']
base_dir = "."

def get_base_dir():
    return os.path.abspath(os.path.join(homedir, base_dir))


pipe = pipeline(task="depth-estimation", model="depth-anything/Depth-Anything-V2-Large-hf")

def rien(masque_bool):
    ax = plt.gca()
    img = np.ones((masque_bool.shape[0], masque_bool.shape[1], 4))
    img[:,:,3] = 0
    color_mask = np.concatenate([[1,0,0], [0.65]])
    img[masque_bool] = color_mask
    ax.imshow(img)
    
def find_discontinuity(data):
  diffs = [data[i+1] - data[i] for i in range(len(data)-1)]
  for i in reversed(range(0,len(diffs))):
    diff = diffs[i]
    if diff != 1:
      return i+1 # Return the index of the element *after* the discontinuity
  return -1

def unique_pair(reg_inside_y,pair_reg):
  reg_unique_pair = []
  for iy in reg_inside_y:
    X_ = []
    for iys,ixs in pair_reg:
      if iy==iys:
        X_.append(ixs)
    median_ = np.median(X_).astype('int')
    reg_unique_pair.append((iy,median_))
  return reg_unique_pair

def centroid_msk(msks):

    msks = msks.astype('uint8')
    L = np.unique(msks)
    L = [ix for ix in L if ix!=0]
    dico = {}
    for label_ix in L:
        msks_ix = np.where(msks==label_ix,255,0)
        msks_ix = msks_ix.astype('uint8')

        moments = cv2.moments(msks_ix) # Trouver les moments de l'image
        # Calculer le centroïde (cx, cy)
        if moments["m00"] != 0:  # Éviter la division par zéro
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            dico[label_ix]=[cx,cy]
        else:
            print("Aucun objet trouvé dans le masque.")
    return dico

def unique_y_values(list_of_tuples):
  seen_y_values = set()
  unique_y_list = []
  for y, x in list_of_tuples:
    if y not in seen_y_values:
      seen_y_values.add(y)
      unique_y_list.append(y)
  return unique_y_list

def top_point_research(curr_reg,x0,y0,lenght):
  coordinates = np.argwhere(curr_reg == 255)[::-1]
  for y, x in coordinates:
    l = np.sqrt((x0-x)**2+(y0-y)**2)
    if l > lenght:
      break
  return y,x
def sem_to_inst_part(msks,ker_size=10,cleared_activation=True):
    msks = msks.astype('uint8')

    kernel = np.ones((ker_size*3, ker_size*3), np.uint8)
    img_dilation = cv2.dilate(msks, kernel, iterations=1)
    img_erosion = cv2.erode(img_dilation, kernel, iterations=1)

    label_image = label(img_erosion) # label image regions
    return label_image

def reattribute_data(data,msks):
  sorted_items = sorted(data.items(), key=lambda item: item[1][0]) # Trier les éléments par la première valeur de chaque liste
  new_dict = {new_key: value for new_key, (_, value) in enumerate(sorted_items, start=1)} # Réattribuer les clés dans l'ordre
  rotation_ = []
  for ix in new_dict:
    cent_r = new_dict[ix][0]
    for iy in data:
      cent_c = data[iy][0]
      if cent_r == cent_c:
        rotation_.append([iy,ix])

  np_z = np.zeros(msks.shape)
  for ix in rotation_:
    np_z = np.where(msks==ix[0],ix[1],np_z)

  return np_z,new_dict

def min_max_reg(reg_unique_pair,reg_inside_y):
  borne_mn_y = None
  borne_mx_y = None

  for ix in reg_unique_pair:
    y_ = ix[0]
    if y_ == min(reg_inside_y):
      borne_mn_y = ix
    if y_ == max(reg_inside_y):
      borne_mx_y = ix
  return borne_mn_y,borne_mx_y

def milieu_droite(borne_mn_y, borne_mx_y):
  milieu_y = (borne_mn_y[0] + borne_mx_y[0]) // 2
  milieu_x = (borne_mn_y[1] + borne_mx_y[1]) // 2
  return (milieu_y, milieu_x)

def diamant_star(curr_reg_one,I):
  coordinates = np.argwhere(curr_reg_one == 255) # col 1 : Y et col2 : X
  y,x = coordinates[:,0],coordinates[:,1]
  my_list = list(zip(y,x))
  unique_y = unique_y_values(my_list)
  discontinuity_index = find_discontinuity(unique_y)
  reg_inside_y = unique_y[discontinuity_index:]

  pair_reg = [(iy,ix) for iy,ix in my_list if iy in reg_inside_y]
  reg_unique_pair = unique_pair(reg_inside_y,pair_reg)
  borne_mn_y,borne_mx_y = min_max_reg(reg_unique_pair,reg_inside_y)
  milieu = milieu_droite(borne_mn_y, borne_mx_y)

  x0 = I[0] #x0
  x1 = I[1] #x1
  xc = I[2] #xcenter
  yc = I[3] #ycenter

  perc = .2
  twenty_percent_of_xc_droite = milieu[1] +  int(perc * (x1-xc))
  twenty_percent_of_xc_gauche = milieu[1] -  int(perc * (xc-x0))

  top = [borne_mn_y[1],borne_mn_y[0]] #xt,yt
  mid = [milieu[1],milieu[0]]
  bottom = [borne_mx_y[1],borne_mx_y[0]]
  mid_droite = [twenty_percent_of_xc_droite,milieu[0]]
  mid_gauche = [twenty_percent_of_xc_gauche,milieu[0]]

  return top,mid,mid_droite,mid_gauche,bottom

def keep_largest_object(binary_image):
    """
    Garde uniquement le plus grand objet dans une image binaire en utilisant OpenCV.

    :param binary_image: Image binaire (0 pour le fond, 255 pour les objets)
    :return: Image filtrée avec uniquement le plus grand objet
    """
    binary_image = binary_image.astype('uint8')
    # Trouver les contours des objets dans l'image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return np.zeros_like(binary_image)  # Si pas d'objets, retourne une image vide

    # Trouver le contour avec la plus grande aire
    largest_contour = max(contours, key=cv2.contourArea)

    # Créer une image vide de la même taille que l'image d'entrée
    filtered_image = np.zeros_like(binary_image)

    # Dessiner le plus grand contour sur l'image filtrée
    cv2.drawContours(filtered_image, [largest_contour], -1, (255), thickness=cv2.FILLED)

    return filtered_image

def area_pts(msks,dico):
    msks = msks.astype('uint8')
    maxX = msks.shape[1]
    X = [0]
    for ix in dico:
        X.append(dico[ix][0])
    X.append(maxX)
    midpoints = [(X[i] + X[i + 1]) / 2 for i in range(len(X) - 1)]
    midpoints[0] = 0
    midpoints[-1] = maxX

    centroid_X = []
    for ix in dico:
        centroid_X.append(dico[ix][0])
        # print(ix,dico[ix][0])
    dicow = {}
    for i,j,z in zip(centroid_X,range(len(midpoints) - 1),dico):
        dicow[z] = [midpoints[j],midpoints[j + 1]]+dico[z] # cle label / valeur espace droite et gauche et cx, cy
        # print(z,dicow[z])
    # print('==')
    return dicow

def regression_label(curr_msk,vis_reg = False,vis_res = False):
  curr_msk = curr_msk.astype('uint8')
  assert curr_msk.ndim==2
  n,m = curr_msk.shape
  coordinates = np.argwhere(curr_msk == 255) # col 1 : Y et col2 : X
  y,x = coordinates[:,0].reshape(-1, 1),coordinates[:,1].reshape(-1, 1)
  curr_reg = curr_msk.copy()
  if len(x) > 1:
    model = LinearRegression()
    model.fit(x, y)


    model.fit(y, x)
    y_or_flat = y.flatten()
    if min(y_or_flat)==0:
      return curr_reg
    y_prediction = np.arange(0,min(y_or_flat)).reshape(-1, 1)
    x_pred = model.predict(y_prediction).flatten()
    if vis_reg:
      plt.scatter(x,y)
      plt.scatter(x_pred,y_prediction)

    x_pred = np.array(x_pred,dtype='int')
    x_pred = np.where(x_pred > m-1,m-1,x_pred)
    y_prediction = y_prediction.flatten()
    y_prediction = np.where(y_prediction > n-1,n-1,y_prediction)
    assert len(x_pred)==len(y_prediction)

    for row,col in zip(x_pred,y_prediction):
      curr_reg[col, row] = 255
  else:
    return curr_reg
  kernel = np.ones((5, 5), np.uint8)
  img_dilation = cv2.dilate(curr_reg, kernel, iterations=1)

  if vis_res:
    plt.imshow(img_dilation,cmap="gray")
  return img_dilation

def calculate_angle(p1, p2, p3):
  """Calculates the angle between three points.

  Args:
    p1: A tuple representing the coordinates of the first point (x1, y1).
    p2: A tuple representing the coordinates of the second point (x2, y2).
    p3: A tuple representing the coordinates of the third point (x3, y3).

  Returns:
    The angle in degrees between the lines p1-p2 and p2-p3.
  """
  x1, y1 = p1
  x2, y2 = p2
  x3, y3 = p3

  # Calculate vectors
  v1 = np.array([x1 - x2, y1 - y2])
  v2 = np.array([x3 - x2, y3 - y2])
  # v2 = np.array([x2 - x3, y2 - y3])

  # Calculate dot product and magnitudes
  dot_product = np.dot(v1, v2)
  magnitude_v1 = np.linalg.norm(v1)
  magnitude_v2 = np.linalg.norm(v2)

  # Calculate cosine of the angle
  cos_angle = dot_product / (magnitude_v1 * magnitude_v2)

  # Handle potential numerical errors
  cos_angle = np.clip(cos_angle, -1, 1)  # Ensure cosine is within valid range

  # Calculate angle in radians and convert to degrees
  angle_rad = np.arccos(cos_angle)
  angle_deg = np.degrees(angle_rad)

  return angle_deg

def angle_regression(x_pred,y_prediction):
  y0,x0 = np.max(y_prediction),x_pred[np.argmax(y_prediction)]
  y1,x1 = np.min(y_prediction),x_pred[np.argmin(y_prediction)]
  p1,p2,p3 = (x1,y1),(x0,y0),(x0,0)
  # print(p1,p2,p3)
  angle_deg = calculate_angle(p1, p2, p3)
  return angle_deg
def outlier_detection(X_study1,L):

  X = np.array(X_study1).reshape(-1, 1)
  # clustering = DBSCAN(eps=10, min_samples=1).fit(X)
  # y_pred = clustering.labels_

  clf = LocalOutlierFactor(n_neighbors=1, contamination=0.1)
  y_pred = clf.fit_predict(X)

  dico_out = {ix : [iy[0],iz] for ix,iy,iz in zip(L,X,y_pred)}
  return dico_out

def angle_assessment(msks):
  msks = msks.astype('uint8')
  L = np.sort([ix for ix in np.unique(msks) if ix!=0])
  L = L.astype('int')

  X_study1 = []
  for curr_label in L:
    curr_msk = np.where(msks==curr_label,255,0)
    curr_reg = regression_label(curr_msk)

    curr_msk = curr_msk.astype('uint8')
    assert curr_msk.ndim==2
    n,m = curr_msk.shape
    coordinates = np.argwhere(curr_msk == 255) # col 1 : Y et col2 : X
    y,x = coordinates[:,0].reshape(-1, 1),coordinates[:,1].reshape(-1, 1)
    curr_reg = curr_msk.copy()
    if len(x) > 1:
      model = LinearRegression()
      model.fit(y, x)
      y_prediction = np.arange(0,min(y.flatten())).reshape(-1, 1)
      x_pred = model.predict(y_prediction).flatten()

      angle_deg = angle_regression(x_pred,y_prediction)
      X_study1.append(180+angle_deg)

  if len(X_study1) == 1:
    dico_out = {}
    dico_out[L[0]]=[X_study1[0],1]
  else:
    dico_out = outlier_detection(X_study1,L)


  M = []
  for ix in dico_out:
    idx_ = dico_out[ix][1]
    if idx_ != -1:
      M.append(dico_out[ix][0])
  for ix in dico_out:
    idx_ = dico_out[ix][1]
    if idx_ == -1:
      dico_out[ix][0] = np.mean(M)
      dico_out[ix][1] = 1
  return dico_out

def regression_with_correction_angle(curr_msk,angle_deg,n,m,vis_reg = False,vis_res = False):

  def new_droite(angle_deg,x_pred,y_prediction):

    def calculate_p1(angle_deg, p2, p3):
        """Calculates p1 given angle, p2, and p3.

        Args:
            angle_deg: The angle between the lines p1-p2 and p2-p3 in degrees.
            p2: A tuple representing the coordinates of the second point (x2, y2).
            p3: A tuple representing the coordinates of the third point (x3, y3).

        Returns:
            A tuple representing the coordinates of the first point (x1, y1).
            Returns None if a solution cannot be found.
        """
        x2, y2 = p2
        x3, y3 = p3
        angle_rad = np.radians(angle_deg)

        # Calculate vector v2
        v2 = np.array([x3 - x2, y3 - y2])

        # Calculate the rotation matrix
        rotation_matrix = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad), np.cos(angle_rad)]
        ])

        # Calculate vector v1
        v1 = np.dot(rotation_matrix, v2)


        # Calculate p1
        x1 = x2 - v1[0]
        y1 = y2 - v1[1]

        return (x1, y1)

    def calculate_p1_on_x_axis(p1, p2, p3):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        m_p1p2 = (y2-y1)/(x2-x1)
        x1_ = x2-y2/m_p1p2
        return x1_

    x0 = max(x_pred)
    y_prediction_ = y_prediction.flatten()
    y0 = max(y_prediction_) 
    p2,p3 = (x0,y0),(x0,0)
    p1_ = calculate_p1(angle_deg, p2, p3)
    p1_x = calculate_p1_on_x_axis(p1_, p2, p3)
    x_n,y_n = p1_x,0 
    return x_n,y_n

  def check1(x_news,y_news):
      x_news1,y_news1 = [],[]
      for x,y in zip(x_news,y_news):
        if x >= 0 and y >= 0:
          x_news1.append(x)
          y_news1.append(y)
        elif x >= 0 and y < 0:
          x_news1.append(x)
          y_news1.append(0)
        elif x < 0 and y >= 0:
          x_news1.append(0)
          y_news1.append(y)
        elif x < 0 and y < 0:
          x_news1.append(0)
          y_news1.append(0)
      return x_news1,y_news1

  def check2(x_news1,y_news1,n,m):
      x_news2,y_news2 = [],[]
      for x,y in zip(x_news1,y_news1):
        if x <= m-1 and y <= n-1:
          x_news2.append(x)
          y_news2.append(y)
        elif x <= m-1 and y > n-1:
          x_news2.append(x)
          y_news2.append(n-1)
        elif x > m-1 and y <= n-1:
          x_news2.append(m-1)
          y_news2.append(y)
        elif x > m-1 and y > n-1:
          x_news2.append(m-1)
          y_news2.append(n-1)
      return x_news2,y_news2

  def tracer_droite(p0, p1):
      x0, y0 = p0
      x1, y1 = p1

      # Calcul des différences
      dx = x1 - x0
      dy = y1 - y0

      # Déterminer le nombre de points
      steps = max(abs(dx), abs(dy))  # Le plus grand déplacement détermine le nombre de points

      # Calcul des incréments
      x_inc = dx / steps
      y_inc = dy / steps

      # Initialisation des points
      x, y = x0, y0
      points = [(round(x), round(y))]

      for _ in range(steps):
          x += x_inc
          y += y_inc
          points.append((round(x), round(y)))  # On arrondit pour obtenir des coordonnées discrètes

      return points

  curr_msk = curr_msk.astype('uint8')

  assert curr_msk.ndim==2
  coordinates = np.argwhere(curr_msk == 255) # col 1 : Y et col2 : X
  y,x = coordinates[:,0].reshape(-1, 1),coordinates[:,1].reshape(-1, 1)
  curr_reg = curr_msk.copy()
  if len(x) > 1:

    y0,x0 = np.max(y),x[np.argmax(y)][0]
    y1,x1 = np.min(y),x[np.argmin(y)][0]

    y0,x0 = np.min(y),x[np.argmin(y)][0]
    y1,x1 = np.max(y),x[np.argmax(y)][0]

    x_pred = x.flatten()
    y_prediction = y.flatten()

    x_n,y_n = new_droite(angle_deg,x_pred,y_prediction)
    p0, p1 = (x0,y0),(x_n,y_n)
    resultat = tracer_droite(p0, p1)

    x_news,y_news = [],[]
    for res_ in resultat:
      x_news.append(res_[0])
      y_news.append(res_[1])
    x_news1,y_news1 = check1(x_news,y_news) # check origin
    x_news2,y_news2 = check2(x_news1,y_news1,n,m) # check border

    for row,col in zip(x_news2,y_news2):
        curr_reg[col, row] = 255

    kernel = np.ones((5, 5), np.uint8)
    img_dilation = cv2.dilate(curr_reg, kernel, iterations=1)
    return img_dilation
  
def curr_sum_one(curr_reg,msks_depth):
  # curr_reg = regression_label(curr_msk)
  curr_reg_one = np.where(curr_reg!=0,145,0)

  msks_depth_one = np.where(msks_depth!=0,145,0)

  curr_sum = curr_reg_one + msks_depth_one
  curr_sum_one = np.where(curr_sum> 145,255,0)
  return curr_sum_one


def minimum_betw_max(dico_,visua=False):
  Ax = list(dico_.keys())
  Ay = list(dico_.values())

  # Approximation par une régression polynomiale
  x = Ax[1:]
  y = Ay[1:]
  degree = 14  # Choisissez le degré selon la complexité de la courbe
  coefficients = np.polyfit(x, y, degree)
  polynomial = np.poly1d(coefficients)

  # Points lissés pour tracer la courbe
  x_fit = np.linspace(min(x), max(x), 500)
  y_fit = polynomial(x_fit)

  # Détection des maxima
  peaks, _ = find_peaks(y_fit)

  peak_values = y_fit[peaks]
  sorted_indices = np.argsort(peak_values)[::-1]  # Trier en ordre décroissant
  top_two_peaks = peaks[sorted_indices[:2]]       # Les indices des deux plus grands pics

  # Trouver le minimum entre les deux maxima
  x_min_range = x_fit[top_two_peaks[0]:top_two_peaks[1]+1]
  y_min_range = y_fit[top_two_peaks[0]:top_two_peaks[1]+1]
  minx = min([top_two_peaks[0],top_two_peaks[1]])
  maxx = max([top_two_peaks[0],top_two_peaks[1]])
  x_min_range = x_fit[minx:maxx+1]
  y_min_range = y_fit[minx:maxx+1]
  min_index = np.argmin(y_min_range)  # Index du minimum dans cette plage
  x_min = x_min_range[min_index]
  y_min = y_min_range[min_index]

  if visua:
    # Tracé
    plt.scatter(x, y, color='blue')
    plt.plot(x_fit, y_fit, color='red', label='Polynomial regression')
    plt.scatter(x_fit[top_two_peaks], y_fit[top_two_peaks], color='green', label='Local maximum')
    plt.scatter(x_min, y_min, color='orange', s=100, label='Local minimum')
    plt.legend()
    plt.xlabel('Depth pixel')
    plt.ylabel('Count')
    # plt.title('Approximation et détection des points maximum')
    plt.show()
  return x_min,y_min


def frontground_part(depths):
    depth_one = depths[:,:]
    n,m = depth_one.shape
    A = []
    for i in tqdm(range(n)):
        for j in range(m):
            A.append([i,j,depth_one[i,j]])
    X = np.array(A)

    dico_ = Counter(X[:,2])
    min_coord = minimum_betw_max(dico_,visua=False)

    th_ = min_coord[0]
    msks_depth = (depth_one > th_)
    return msks_depth
