import os
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

import utils.utils as utils
from net.inception import InceptionResNetV1
from net.mtcnn import mtcnn


class FaceRecognitionService:
    def __init__(self):
        """初始化人脸识别服务"""
        #-------------------------#
        #   创建mtcnn的模型
        #   用于检测人脸
        #-------------------------#
        self.mtcnn_model = mtcnn()
        self.threshold = [0.5, 0.6, 0.8]
               
        #-----------------------------------#
        #   载入facenet
        #   将检测到的人脸转化为128维的向量
        #-----------------------------------#
        self.facenet_model = InceptionResNetV1()
        # 获取当前脚本文件的目录，构建模型文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'model_data', 'facenet_keras.h5')
        self.facenet_model.load_weights(model_path)

        #-----------------------------------------------#
        #   对数据库中的人脸进行编码
        #   known_face_encodings中存储的是编码后的人脸
        #   known_face_names为人脸的名字
        #-----------------------------------------------#
        self.known_face_encodings = []
        self.known_face_names = []
        
        # 置信度计算参数
        self.confidence_config = {
            'method': 'piecewise_linear',  # 置信度计算方法
            'max_distance': 1.2,          # 最大距离阈值
            'quality_boost': True,        # 是否启用质量提升
        }
        
        self.load_face_database()

    def load_face_database(self):
        """加载人脸数据库"""
        self.known_face_encodings = []
        self.known_face_names = []
        
        # 获取当前脚本文件的目录，构建face_dataset的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        face_dataset_dir = os.path.join(current_dir, "face_dataset")
        
        if not os.path.exists(face_dataset_dir):
            os.makedirs(face_dataset_dir)
            return
            
        face_list = os.listdir(face_dataset_dir)
        for face in face_list:
            name = face.split(".")[0]
            img_path = os.path.join(face_dataset_dir, face)
            img = cv2.imread(img_path)
            if img is None:
                continue
            
            encoding = self._encode_face(img)
            if encoding is not None:
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(name)

    def _encode_face(self, img):
        """对单张人脸图片进行编码"""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        #---------------------#
        #   检测人脸
        #---------------------#
        rectangles = self.mtcnn_model.detectFace(img_rgb, self.threshold)
        if len(rectangles) == 0:
            return None
            
        #---------------------#
        #   转化成正方形
        #---------------------#
        rectangles = utils.rect2square(np.array(rectangles))
        rectangle = rectangles[0]
        
        # 修正边界框，确保在图片范围内
        height, width = img_rgb.shape[:2]
        x1 = max(0, int(rectangle[0]))
        y1 = max(0, int(rectangle[1]))
        x2 = min(width-1, int(rectangle[2]))
        y2 = min(height-1, int(rectangle[3]))
        
        # 检查边界框是否有效
        if x1 >= x2 or y1 >= y2:
            return None
        
        # 重新计算landmark相对位置
        landmark = np.reshape(rectangle[5:15], (5, 2)) - np.array([x1, y1])
        crop_img = img_rgb[y1:y2, x1:x2]
        
        if crop_img.size == 0:
            return None
            
        crop_img, _ = utils.Alignment_1(crop_img, landmark)
        crop_img = np.expand_dims(cv2.resize(crop_img, (160, 160)), 0)
        
        #--------------------------------------------------------------------#
        #   将检测到的人脸传入到facenet的模型中，实现128维特征向量的提取
        #--------------------------------------------------------------------#
        face_encoding = utils.calc_128_vec(self.facenet_model, crop_img)
        return face_encoding

    def register_face(self, image_data, name):
        """
        注册新人脸
        Args:
            image_data: 图片数据 (numpy array 或 base64字符串)
            name: 人脸名称
        Returns:
            dict: 注册结果
        """
        try:
            # 处理输入图片
            if isinstance(image_data, str):
                # base64字符串
                image_data = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_data))
                img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                # numpy array
                img = image_data
            
            # 编码人脸
            encoding = self._encode_face(img)
            if encoding is None:
                return {"success": False, "message": "未检测到人脸"}
            
            # 保存图片到数据库
            current_dir = os.path.dirname(os.path.abspath(__file__))
            face_dataset_dir = os.path.join(current_dir, "face_dataset")
            face_path = os.path.join(face_dataset_dir, f"{name}.jpg")
            cv2.imwrite(face_path, img)
            
            # 添加到内存数据库
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(name)
            
            return {"success": True, "message": f"成功注册人脸: {name}"}
            
        except Exception as e:
            return {"success": False, "message": f"注册失败: {str(e)}"}

    def recognize_face(self, image_data):
        """
        识别人脸
        Args:
            image_data: 图片数据 (numpy array 或 base64字符串)
        Returns:
            dict: 识别结果
        """
        try:
            # 处理输入图片
            if isinstance(image_data, str):
                # base64字符串
                image_data = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_data))
                img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                # numpy array
                img = image_data
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            #--------------------------------#
            #   检测人脸
            #--------------------------------#
            rectangles = self.mtcnn_model.detectFace(img_rgb, self.threshold)
            
            if len(rectangles) == 0:
                return {"success": False, "message": "未检测到人脸", "faces": []}
            
            # 转化成正方形
            rectangles = utils.rect2square(np.array(rectangles))
            
            #-----------------------------------------------#
            #   对检测到的人脸进行编码
            #-----------------------------------------------#
            face_encodings = []
            for rectangle in rectangles:
                #---------------#
                #   截取图像
                #---------------#
                landmark = np.reshape(rectangle[5:15], (5, 2)) - np.array([int(rectangle[0]), int(rectangle[1])])
                crop_img = img_rgb[int(rectangle[1]):int(rectangle[3]), int(rectangle[0]):int(rectangle[2])]
                
                #-----------------------------------------------#
                #   利用人脸关键点进行人脸对齐
                #-----------------------------------------------#
                crop_img, _ = utils.Alignment_1(crop_img, landmark)
                crop_img = np.expand_dims(cv2.resize(crop_img, (160, 160)), 0)
                
                face_encoding = utils.calc_128_vec(self.facenet_model, crop_img)
                face_encodings.append(face_encoding)
            
            # 识别每个人脸
            faces = []
            for i, face_encoding in enumerate(face_encodings):
                #-------------------------------------------------------#
                #   取出一张脸并与数据库中所有的人脸进行对比，计算得分
                #-------------------------------------------------------#
                matches = utils.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.8)
                name = "Unknown"
                confidence = 0.0
                
                if len(self.known_face_encodings) > 0:
                    #-------------------------------------------------------#
                    #   找出距离最近的人脸
                    #-------------------------------------------------------#
                    face_distances = utils.face_distance(self.known_face_encodings, face_encoding)
                    #-------------------------------------------------------#
                    #   取出这个最近人脸的评分
                    #-------------------------------------------------------#
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        # 优化后的置信度计算 (距离越小，置信度越高)
                        confidence = self._calculate_optimized_confidence(face_distances[best_match_index])
                
                # 获取人脸位置
                rectangle = rectangles[i]
                face_info = {
                    "name": name,
                    "confidence": float(confidence),
                    "bbox": {
                        "x1": int(rectangle[0]),
                        "y1": int(rectangle[1]),
                        "x2": int(rectangle[2]),
                        "y2": int(rectangle[3])
                    }
                }
                faces.append(face_info)
            
            return {"success": True, "message": f"检测到{len(faces)}个人脸", "faces": faces}
            
        except Exception as e:
            return {"success": False, "message": f"识别失败: {str(e)}", "faces": []}
    
    def _calculate_optimized_confidence(self, distance):
        """
        优化的置信度计算方法
        使用分段线性函数，显著提高置信度
        """
        method = self.confidence_config.get('method', 'piecewise_linear')
        
        if method == 'piecewise_linear':
            return self._piecewise_linear_confidence(distance)
        elif method == 'sigmoid':
            return self._sigmoid_confidence(distance)
        elif method == 'exponential':
            return self._exponential_confidence(distance)
        else:
            # 默认使用分段线性方法
            return self._piecewise_linear_confidence(distance)
    
    def _piecewise_linear_confidence(self, distance):
        """
        分段线性置信度计算 - 高置信度版本
        针对不同距离区间使用不同的斜率，最大化置信度
        """
        if distance <= 0.25:
            # 优秀匹配: 0.90-1.0 (距离0.25时置信度0.90)
            confidence = 0.90 + (0.25 - distance) / 0.25 * 0.10
        elif distance <= 0.4:
            # 良好匹配: 0.80-0.90 (距离0.4时置信度0.80)
            confidence = 0.80 + (0.4 - distance) / 0.15 * 0.10
        elif distance <= 0.55:
            # 一般匹配: 0.70-0.80 (距离0.55时置信度0.70)
            confidence = 0.70 + (0.55 - distance) / 0.15 * 0.10
        elif distance <= 0.7:
            # 可接受匹配: 0.60-0.70 (距离0.7时置信度0.60)
            confidence = 0.60 + (0.7 - distance) / 0.15 * 0.10
        else:
            # 较差匹配: 0.4-0.60 (距离1.0时置信度0.4)
            confidence = max(0.4, 0.60 - (distance - 0.7) / 0.3 * 0.20)
        
        return min(max(confidence, 0), 1.0)
    
    def _sigmoid_confidence(self, distance, steepness=8, midpoint=0.35):
        """
        Sigmoid函数置信度计算 - 高置信度版本
        在中等距离时提供更高的置信度
        """
        import math
        sigmoid = 1 / (1 + math.exp(-steepness * (midpoint - distance)))
        # 将Sigmoid结果映射到更高的置信度范围
        return 0.3 + sigmoid * 0.7  # 映射到0.3-1.0范围
    
    def _exponential_confidence(self, distance, decay_rate=2.0):
        """
        指数衰减置信度计算 - 高置信度版本
        距离小时置信度快速上升
        """
        import math
        confidence = math.exp(-decay_rate * distance)
        # 将指数结果映射到更高的置信度范围
        return 0.4 + confidence * 0.6  # 映射到0.4-1.0范围
    
    def set_confidence_method(self, method):
        """
        设置置信度计算方法
        可选方法: 'piecewise_linear', 'sigmoid', 'exponential'
        """
        if method in ['piecewise_linear', 'sigmoid', 'exponential']:
            self.confidence_config['method'] = method
            print(f"置信度计算方法已设置为: {method}")
        else:
            print(f"不支持的方法: {method}，请使用: piecewise_linear, sigmoid, exponential")

    def get_face_list(self):
        """获取已注册的人脸列表"""
        return {"success": True, "faces": self.known_face_names}

    def delete_face(self, name):
        """删除指定人脸"""
        try:
            if name in self.known_face_names:
                index = self.known_face_names.index(name)
                self.known_face_names.pop(index)
                self.known_face_encodings.pop(index)
                
                # 删除文件
                current_dir = os.path.dirname(os.path.abspath(__file__))
                face_dataset_dir = os.path.join(current_dir, "face_dataset")
                
                for ext in ['.jpg', '.png', '.jpeg']:
                    face_path = os.path.join(face_dataset_dir, f"{name}{ext}")
                    if os.path.exists(face_path):
                        os.remove(face_path)
                        break
                
                return {"success": True, "message": f"成功删除人脸: {name}"}
            else:
                return {"success": False, "message": f"未找到人脸: {name}"}
        except Exception as e:
            return {"success": False, "message": f"删除失败: {str(e)}"}