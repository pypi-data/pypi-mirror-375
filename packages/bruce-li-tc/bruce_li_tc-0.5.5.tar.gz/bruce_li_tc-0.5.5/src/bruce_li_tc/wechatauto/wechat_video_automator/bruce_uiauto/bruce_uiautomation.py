from typing import List, Dict, Any
import pyautogui
import uiautomation as auto
import time
import re
import subprocess
from typing import Optional
from pathlib import Path
import importlib.resources
from .bruce_auto_log import library_logger

class WeChat_Auto_utils:
    def __init__(self):
        pass

    def find_sibling_tabs(self,name: str):
        """
        查找指定名称的标签页的兄弟节点（上一个和下一个）。
        :param name: 要查找的标签页的名称
        :return:
        """
        try:
            # 首先定位到目标标签页控件
            current_tab = auto.TabItemControl(Name=name)

            if not current_tab.Exists(maxSearchSeconds=10):
                library_logger.info(f"未找到名为 '{name}' 的标签页控件")
                return None, None

            # 获取上一个兄弟节点
            previous_sibling = current_tab.GetPreviousSiblingControl()

            # 获取下一个兄弟节点
            next_sibling = current_tab.GetNextSiblingControl()

            """
            用以下方法来导航和查找控件：
            获取上一个兄弟节点       control.GetPreviousSiblingControl()  返回同一层级中位于当前控件之前的控件对象，若不存在则返回 None
            获取下一个兄弟节点       control.GetNextSiblingControl()     返回同一层级中位于当前控件之后的控件对象，若不存在则返回 None
            获取所有直接子节点的列表  control.GetChildren()               返回一个包含所有直接子控件对象的列表  
            获取父节点             control.GetParentControl()           返回当前控件的父控件对象
            """
            return previous_sibling, next_sibling

        except Exception as e:
            library_logger.info(f"查找兄弟节点时出错: {e}")
            return None, None
    def find_and_filter_children(self,parent_control, target_name: str = None, is_click=True):
        """
        查找父控件的所有直接子节点，并根据条件进行筛选。
        :param parent_control:父控件对象
        :param target_name:(可选) 要筛选的子节点名称。如果为None，则打印所有子节点信息。
        :return:
        """
        try:
            # 获取父控件的所有直接子节点
            children = parent_control.GetChildren()
            library_logger.info(f"  正在检查父控件 '{parent_control.Name}' 的子节点 (共{len(children)}个)...")

            for child in children:
                # 如果没有指定目标名称，则打印所有子节点信息
                if target_name is None:
                    library_logger.info(f"    - 子节点名称: '{child.Name}', 控件类型: '{child.ControlTypeName}'")
                else:
                    # 如果指定了目标名称，则进行匹配
                    if child.Name == target_name:
                        library_logger.info(f"    ✓ 找到目标子节点: '{child.Name}', 控件类型: '{child.ControlTypeName}'")
                        if is_click:
                            child.Click()
                        # child.Click()
                        return child  # 如果需要返回找到的控件，可以取消注释
        except Exception as e:
            library_logger.info(f"  获取或遍历子节点时发生错误: {e}")
    def is_control_clickable(self,control):
        """
         综合判断控件是否可点击
        Args:
            control: uiautomation 控件对象
        Returns:
            bool: True 表示可点击，False 表示不可点击
        """
        if control is None:
            return False
            # 检查控件是否存在
        if not control.Exists(maxSearchSeconds=1):
            return False
        # 获取控件的边界矩形
        rect = control.BoundingRectangle
        # 检查边界矩形是否有效（非零且宽度高度为正）
        if rect.width() <= 0 or rect.height() <= 0:
            return False
        if rect.left == 0 and rect.top == 0 and rect.right == 0 and rect.bottom == 0:
            return False
        # 检查控件是否在屏幕外
        if control.IsOffscreen:
            return False
        return True

class Automator_utils:

    @staticmethod
    def _get_control_type_name(control_type: int) -> str:
        """
        将控件类型ID转换为可读的名称
        """
        # 使用控件类型的整数值进行映射，避免直接访问ControlType的属性
        control_type_map = {
            50000: "Button",
            50001: "Calendar",
            50002: "CheckBox",
            50003: "ComboBox",
            50004: "Custom",
            50005: "DataGrid",
            50006: "DataItem",
            50007: "Document",
            50008: "Edit",
            50009: "Group",
            50010: "Header",
            50011: "HeaderItem",
            50012: "Hyperlink",
            50013: "Image",
            50014: "List",
            50015: "ListItem",
            50016: "Menu",
            50017: "MenuBar",
            50018: "MenuItem",
            50019: "Pane",
            50020: "ProgressBar",
            50021: "RadioButton",
            50022: "ScrollBar",
            50023: "SemanticZoom",
            50024: "Separator",
            50025: "Slider",
            50026: "Spinner",
            50027: "SplitButton",
            50028: "StatusBar",
            50029: "Tab",
            50030: "TabItem",
            50031: "Table",
            50032: "Text",
            50033: "Thumb",
            50034: "TitleBar",
            50035: "ToolBar",
            50036: "ToolTip",
            50037: "Tree",
            50038: "TreeItem",
            50039: "Window"
        }

        return control_type_map.get(control_type, f"Unknown({control_type})")
    @staticmethod
    def _safe_get_control_attribute(control, attr_name, default=None):
        try:
            return getattr(control, attr_name)
        except Exception:
            return default
    @staticmethod
    def explore_controls(wechat_window, max_depth: int = 5) -> List[Dict[str, Any]]:
        """
        探索微信窗口中的所有控件，返回控件信息列表

        Args:
            max_depth: 最大探索深度

        Returns:
            包含控件信息的字典列表
        """
        if not wechat_window:
            pass

        controls_info = []

        def _explore_recursive(parent, depth):
            if depth > max_depth:
                return

            try:
                children = parent.GetChildren()
                for child in children:
                    try:
                        # 获取控件信息
                        control_info = {
                            'depth': depth,
                            'name': Automator_utils._safe_get_control_attribute(child, 'Name', ''),
                            'control_type': Automator_utils._get_control_type_name(
                                Automator_utils._safe_get_control_attribute(child, 'ControlType', 0)),
                            'automation_id': Automator_utils._safe_get_control_attribute(child, 'AutomationId', ''),
                            'class_name': Automator_utils._safe_get_control_attribute(child, 'ClassName', ''),
                            'is_enabled': Automator_utils._safe_get_control_attribute(child, 'IsEnabled', False),
                            'is_visible': not Automator_utils._safe_get_control_attribute(child, 'IsOffscreen', True),
                            'bounding_rectangle': Automator_utils._safe_get_control_attribute(child, 'BoundingRectangle', (0, 0, 0, 0)),
                            'process_id': Automator_utils._safe_get_control_attribute(child, 'ProcessId', 0),
                            'runtime_id': Automator_utils._safe_get_control_attribute(child, 'RuntimeId', []),  # 安全访问RuntimeId
                            'control': child
                        }

                        controls_info.append(control_info)

                        # 递归探索子控件
                        _explore_recursive(child, depth + 1)

                    except Exception as e:
                        # 忽略无法访问的控件
                        error_info = {
                            'depth': depth,
                            'name': f'ERROR: {str(e)}',
                            'control_type': 'Unknown',
                            'automation_id': '',
                            'class_name': '',
                            'is_enabled': False,
                            'is_visible': False,
                            'bounding_rectangle': (0, 0, 0, 0),
                            'process_id': 0,
                            'runtime_id': [],
                            'control': None
                        }
                        controls_info.append(error_info)
                        continue

            except Exception as e:
                # 处理获取子控件时的异常
                error_info = {
                    'depth': depth,
                    'name': f'ERROR getting children: {str(e)}',
                    'control_type': 'Unknown',
                    'automation_id': '',
                    'class_name': '',
                    'is_enabled': False,
                    'is_visible': False,
                    'bounding_rectangle': (0, 0, 0, 0),
                    'process_id': 0,
                    'runtime_id': [],
                    'control': None
                }
                controls_info.append(error_info)

        # 开始探索
        _explore_recursive(wechat_window, 0)
        return controls_info

    @staticmethod
    def log_control_tree(controls_info: List[Dict[str, Any]]):
        """
        以树形结构打印控件信息

        Args:
            controls_info: 控件信息列表
        """
        library_logger.info("controls_info", controls_info)
        region = None
        for info in controls_info:
            indent = "  " * info['depth']
            library_logger.info(f"{indent}[{info['control_type']}] {info['name']}")
            library_logger.info(f"{indent}  AutomationId: {info['automation_id']}")
            library_logger.info(f"{indent}  ClassName: {info['class_name']}")
            library_logger.info(f"{indent}  Enabled: {info['is_enabled']}, Visible: {info['is_visible']}")
            library_logger.info(f"{indent}  Bounds: {info['bounding_rectangle']}")
            library_logger.info(f"{indent}  ProcessId: {info['process_id']}")
            region = info['bounding_rectangle']
        return region

    @staticmethod
    def find_and_click_template(template_path, region=None, confidence=0.7, max_retries=3, retry_interval=1.0):
        """
        在屏幕上查找模板图片，找到后点击其中心位置。

        Args:
            template_path (str): 模板图片的路径
            region (tuple, optional): 搜索区域 (left, top, width, height)。默认为全屏。
            confidence (float, optional): 匹配置信度，0-1之间。越高越严格。
            max_retries (int, optional): 最大重试次数。
            retry_interval (float, optional): 重试间隔（秒）。

        Returns:
            bool: 成功找到并点击返回True，否则返回False。
        """
        for attempt in range(max_retries):
            try:
                # 使用pyautogui的locateOnScreen函数进行图像识别
                location = pyautogui.locateOnScreen(template_path, region=region, confidence=confidence)

                if location is not None:
                    center = pyautogui.center(location)
                    pyautogui.click(center)
                    library_logger.info(f"成功点击模板：{template_path}，位置：{center}")
                    return True
                else:
                    library_logger.info(f"第{attempt + 1}次尝试未找到模板：{template_path}，将在{retry_interval}秒后重试")
                    time.sleep(retry_interval)

            except pyautogui.ImageNotFoundException:
                library_logger.info(f"第{attempt + 1}次尝试未找到模板（ImageNotFoundException）：{template_path}")
                time.sleep(retry_interval)
            except Exception as e:
                library_logger.info(f"在查找模板 {template_path} 时发生未知错误: {e}")
                break

        library_logger.info(f"已达到最大重试次数 {max_retries}，未能找到并点击 {template_path}")
        return False

class WeChat_VideoData_utils:
    def extract_number_from_string(self,s):
        """
        从字符串中提取数字部分，支持整数、小数和带'万'或'万+'的数字。
        会尽量保留原始格式（如包含'万'或'万+'字），仅在无数字时返回"0"。

        参数:
            s (str): 输入的字符串，例如"喜欢，170", "分享，17万", "点赞, 8.8万", "喜欢10万+"

        返回:
            str: 提取出的数字字符串。如果没有数字则返回"0"。
        """
        # 匹配模式：数字（可能含小数点）+可能紧跟的'万'字+可能紧跟的'+'号
        pattern = r'\d+\.?\d*\s*万\+?|\d+\.?\d+|\b\d+\b'
        matches = re.findall(pattern, s)

        if not matches:
            return "0"

        # 取第一个匹配项
        matched_str = matches[0]

        # 移除数字和单位之间的任何空格（保留原始格式但规范化）
        matched_str = re.sub(r'(\d)\s*万', r'\1万', matched_str)

        return matched_str

class WeChatAutomator:
    """微信自动化示例类"""

    def __init__(self):
        """
        微信窗口和微信窗格独立分开的，微信主页面就是窗口，打开其他页面就是窗格
        """
        self.WECHAT_WINDOW = None#微信窗口
        self.WECHAT_PANE=None#微信窗格
        self.TEXT_CONTROL= None#视频号里面的"动态"文本控件
        self.IS_GLOBAL_SEARCH=False #是否全局搜索
        self.SEARCH_KEYWORD=None#视频号搜索关键字
        self.AutomatorUtils=Automator_utils()
        self.WeChat_Auto_utils=WeChat_Auto_utils()
        self.WeChat_VideoData_utils=WeChat_VideoData_utils()
        self.comment_callback = None # 初始化回调函数为None
    def start_webchat(self,wechat_path: str=r"C:\Program Files\Tencent\Weixin\Weixin.exe") -> Optional[int]:
        """
        启动微信并返回其进程PID

        Args:
            wechat_path (str): 微信客户端的完整路径

        Returns:
            Optional[int]: 成功则返回进程PID，失败则返回None
        """
        try:
            # 使用subprocess.Popen启动进程，并获取进程对象
            process = subprocess.Popen([wechat_path])
            library_logger.info(f"微信启动成功，PID: {process.pid}")
            return process.pid
        except FileNotFoundError:
            library_logger.warning(f"错误：未找到微信程序，请检查路径 '{wechat_path}' 是否正确")
        except Exception as e:
            library_logger.warning(f"启动微信时发生未知错误: {e}")
        return None
    def search_wechat(self):
        """打开微信,并激活窗口"""
        library_logger.info("查找微信窗口")
        try:
            self.WECHAT_WINDOW = auto.WindowControl(Name="微信")
            # 这里应该是启动微信的逻辑

            if not self.WECHAT_WINDOW.Exists(maxSearchSeconds=10):
                library_logger.info("未找到微信主窗口")
                return False
            else:
                library_logger.info("已找到微信主窗口")

            # 激活窗口确保可见
            self.WECHAT_WINDOW.SetFocus()
            time.sleep(1)
            return True
        except Exception as e:
            library_logger.info(f"查找微信窗口失败: {e}")
            return False
    def open_video_channel(self):
        """点击打开视频号"""
        library_logger.info("点击打开视频号窗口")
        try:
            # 这里应该是打开视频频道的逻辑
            # 例如，点击微信主窗口的"视频"按钮
            controls_info = self.AutomatorUtils.explore_controls(self.WECHAT_WINDOW, max_depth=20)
            #weixin_controls_bounds = self.AutomatorUtils.log_control_tree(controls_info)
            #library_logger.info()(f"微信客户端坐标", weixin_controls_bounds)
            library_logger.info(f"对微信客户端区域实行图像识别")
            #template_path = r"./video_channel_icon.png"  # 请替换为你的实际路径


            with importlib.resources.path('wechatauto.wechat_video_automator.bruce_uiauto','video_channel_icon.png') as template_path:
            # 调用图像识别函数进行点击
                wechat_region = ()
                success = self.AutomatorUtils.find_and_click_template(str(template_path), region=wechat_region, confidence=0.8)
            if success:
                library_logger.info("成功点击视频号频道")
                time.sleep(2)  # 等待页面加载
                return True
            else:
                library_logger.warning("无法找到视频号图标")
                return False
        except Exception as e:
            library_logger.info(f"点击打开视频号窗口失败: {e}")
            return False
    def find_video_channel(self):
        """
        查找视频号窗口
        注:要在微信窗格下查找比较安全一点，如果查不到再换全局查找
        is_global_search=False #不在全局查找
        is_global_search=True #在全局查找
        :return:
        """
        try:
            library_logger.info("开始查找视频号窗口......")
            self.WECHAT_PANE = auto.PaneControl(ClassName='Chrome_WidgetWin_0', Name='微信')
            if self.WECHAT_PANE.Exists(maxSearchSeconds=3):
                library_logger.info("成功找到微信主窗格")
                # 2. 在找到的微信窗格内，查找名为"动态"的文本控件
                # 使用searchFromControl参数将搜索范围限制在这个窗格内
            else:
                library_logger.info("未找到微信主窗格")
            if self.IS_GLOBAL_SEARCH:
                viedo_account_window = auto.DocumentControl(Name="视频号",ClassName="Chrome_RenderWidgetHostHWND")  # 来自Inspect信息
            else:
                viedo_account_window = auto.DocumentControl(searchFromControl=self.WECHAT_PANE ,Name="视频号",ClassName="Chrome_RenderWidgetHostHWND")  # 来自Inspect信息
            if not viedo_account_window.Exists(maxSearchSeconds=60):
                library_logger.info("未找到视频号窗口")
                return False
            else:
                library_logger.info("已找到视频号窗口")
                return True
            # 打印窗口信息进行确认（类似于您提供的属性）
            # library_logger.info()(f"视频号窗口名: {viedo_account_window.Name}")
            # library_logger.info()(f"视频号自动化ID: {viedo_account_window.AutomationId}")  # 可能为None
            # library_logger.info()(f"视频号类名: {viedo_account_window.ClassName}")
            # library_logger.info()(f"视频号控件类型: {viedo_account_window.ControlType}")
            # library_logger.info()(f"视频号位置和大小: {viedo_account_window.BoundingRectangle}")  # 类似Location
        except Exception as e:
            library_logger.info("找视频号窗口失败",e)
            return False
    def input_keyword_search(self,search_keyword:str):
        """
        视频号-输入关键字并搜索
        :param search_keyword:
        :return:
        """
        try:
            # 这里需要优化在指定区域对比搜索框
            # template_path = r"./search_input.png"
            # wechat_region = () #默认是全屏，可以指定范围进行查找
            # success = self.AutomatorUtils.find_and_click_template(template_path, region=wechat_region, confidence=0.8)
            with importlib.resources.path('wechatauto.wechat_video_automator.bruce_uiauto','search_input.png') as template_path:
                wechat_region = ()  # 默认是全屏，可以指定范围进行查找
                success = self.AutomatorUtils.find_and_click_template(str(template_path), region=wechat_region,confidence=0.8)
            if success:
                library_logger.info("成功点击视频号搜索框")
                time.sleep(2)  # 等待页面加载
            else:
                library_logger.warning("无法点击视频号搜索框")
            try:
                library_logger.info("开始输入关键字并回车......")
                #search_keyword = "阅兵"
                # 直接向当前激活的控件发送按键消息
                self.SEARCH_KEYWORD=search_keyword
                auto.SendKeys(search_keyword + "{Enter}")  # 使用 {Enter} 模拟回车键
                # auto.SendKeys(search_keyword)  # 如果不想立即回车，只输入关键字
                library_logger.info(f"已输入关键字: {search_keyword}")
            except Exception as e:
                library_logger.warning(f"点击视频号搜索框,输入关键字并回车时发生错误: {e}")
            return True
        except Exception as e:
            library_logger.info(f"点击视频号里面的搜索控件时发生错误: {e}")
            return False
    def video_channel_lodding(self):
        """
        视频号-搜索关键字-判断加载是否完成，，如果出现动态两个字就是加载完成了，但是也不能一直等
        #  --情况1:判断当前窗体内是否有动态,有就是加载完成了
        #  --情况2:暂无搜索结果,那就关闭这个标签页重新搜(先不考虑)
        :return:
        """
        try:
            while True:
                self.TEXT_CONTROL = auto.TextControl(searchFromControl=self.WECHAT_PANE, Name="动态")
                if self.TEXT_CONTROL.Exists(maxSearchSeconds=3):
                    library_logger.info("成功在微信窗格内找到'动态'文本控件")
                    self.TEXT_CONTROL.Click()  # 如果支持点击操作
                    return True
                    # rect = text_control.BoundingRectangle
                    # # 打印坐标信息
                    # library_logger.info()(f"控件坐标: left={rect.left}, top={rect.top}, right={rect.right}, bottom={rect.bottom}")
                    # # 计算中心点坐标（如果需要点击等操作）
                    # center_x = (rect.left + rect.right) // 2
                    # center_y = (rect.top + rect.bottom) // 2
                    # library_logger.info()(f"中心点坐标: ({center_x}, {center_y})")
                else:
                    library_logger.warning("在微信窗格内未找到'动态'文本控件")
                time.sleep(1)
        except Exception as e:
            library_logger.warning(f"判断视频号加载完成时发生错误: {e}")
            return False
    def video_list_data(self,skip_comment=False)->list:
        """
        视频号-搜索关键字-判断加载是否完成-找到视频列表
        skip_comment是否跳过不获取评论数据，默认不获取评论数据，只获取视频标题的数据
        :return:
        """

        try:
            parent_group = self.TEXT_CONTROL.GetParentControl()
            # # 2. 获取该父控件的下一个兄弟节点（我们推测它就是视频容器）
            target_video_group = parent_group.GetNextSiblingControl()
            if target_video_group.Exists(maxSearchSeconds=3):
                library_logger.info("成功找到视频容器组")
                data=self.video_item_scroll_click(target_video_group,skip_comment)
                return data
            else:
                library_logger.warning("未找到视频容器组")
        except Exception as e:
            library_logger.warning(f"判断视频号加载完成-找到视频列表时发生错误: {e}")
            return  []
    def video_item_scroll_click(self,target_video_group,skip_comment,max_attempts=10):
        """
        视频号-搜索关键字-判断加载是否完成-找到视频列表-滚动-自动点击
         max_attempts = 10  # 最大尝试滚动次数
        :return:
        """
        max_sib = 0
        # 我们将从第一个视频容器开始处理，temp初始化为target_video_group
        temp = target_video_group
        video_data=[]
        while True:
            try:
                # 对于第一个视频容器(max_sib == 0)，我们不需要获取下一个兄弟控件，因为temp已经是它了
                # 对于后续的(max_sib >= 1)，我们需要获取下一个兄弟控件
                attempt_count = 0  # 第几次滚动
                clicked = False  # 是否可点击
                if max_sib >= 1:
                    temp = temp.GetNextSiblingControl()
                    if temp.Name == "没有更多了":
                        library_logger.info(f"没有更多了,结束点击,总共有{max_sib}个视频容器,循环结束")
                        break
                    if not temp.Exists(maxSearchSeconds=1):  # 检查控件是否存在，等待最多1秒
                        library_logger.info(f"总共有{max_sib + 1} 个视频容器，已经没有找到更多的兄弟标签页，循环终止")
                        break
                while attempt_count < max_attempts and not clicked:
                    temp_click_status = self.WeChat_Auto_utils.is_control_clickable(temp)
                    library_logger.info(f"第 {max_sib + 1} 个视频容器点击状态: {temp_click_status}")
                    if temp_click_status:
                        try:
                            temp.Click(ratioX=0.001, ratioY=0.001)
                            library_logger.info(f"成功点击第 {max_sib + 1} 个视频容器")
                            clicked = True
                            time.sleep(1)  # 等待UI响应
                            item_video_data=self.comment_func(self.WECHAT_PANE)  # 假设comment_func返回True表示完成，False表示未完成/失败
                            video_data.append(item_video_data)

                            # 如果不跳过评论且设置了回调函数，则获取评论数据
                            if skip_comment and self.comment_callback:
                                try:
                                    # self.video_item_comment(next_sibling)
                                    previous_sibling, next_sibling = self.WeChat_Auto_utils.find_sibling_tabs(self.SEARCH_KEYWORD + "_搜索")
                                    # 传递视频数据给评论处理函数，以便回调时能关联评论和视频
                                    self.video_item_comment(next_sibling, item_video_data)
                                except Exception as e:
                                    print(f"第 {max_sib + 1} 个视频容器 获取评论失败: {str(e)}")

                        except Exception as click_error:
                            library_logger.info(f"第 {max_sib + 1} 个视频容器 点击操作失败: {str(click_error)}")
                            # 即使控件可点击，实际点击可能仍会失败，考虑滚动后重试
                            attempt_count += 1
                    else:
                        library_logger.info(f"第 {max_sib + 1} 个视频容器不可点击，尝试滚动 (尝试 {attempt_count + 1}/{max_attempts})")
                        # 执行滚动操作 - 这里需要你实现具体的滚动逻辑
                        self.scroll_video_container(self.SEARCH_KEYWORD)  # 假设你有一个滚动函数
                        attempt_count += 1
                        time.sleep(1.5)  # 等待滚动后内容加载
                # 如果最大尝试次数后仍未点击成功，跳出循环
                if not clicked:
                    library_logger.info(
                        f"第 {max_sib + 1} 个视频容器，经过 {max_attempts} 次尝试仍无法点击第 {max_sib + 1} 个视频，终止处理")
                    max_sib += 1
                    continue

                # 点击成功后的处理（关闭标签页等）
                try:
                    previous_sibling, next_sibling = self.WeChat_Auto_utils.find_sibling_tabs(self.SEARCH_KEYWORD + "_搜索")
                    self.WeChat_Auto_utils.find_and_filter_children(next_sibling, "关闭")
                    library_logger.info(f"第 {max_sib + 1} 个视频容器已关闭标签页")
                except Exception as close_error:
                    library_logger.warning(f"第 {max_sib + 1} 个视频容器 关闭操作失败: {str(close_error)}")
                max_sib += 1
            except Exception as e:
                library_logger.warning(f"在处理第 {max_sib + 1} 个操作时发生错误: {str(e)}")

        return video_data
    def scroll_video_container(self,search_keyword: str):
        """
        尝试滚动视频容器
        返回布尔值表示是否滚动成功
        """
        try:
            scroll_container = auto.DocumentControl(searchDepth=8, Name=search_keyword + '_搜索')  # 根据你的查找条件调整
            if scroll_container.Exists():
                rect = scroll_container.BoundingRectangle
                if rect.width() > 0 and rect.height() > 0:
                    # 计算文档控件的中心坐标
                    center_x = (rect.left + rect.right) // 2
                    center_y = (rect.top + rect.bottom) // 2

                    # 将鼠标移动到该中心点（确保操作焦点在目标区域）
                    auto.MoveTo(center_x, center_y)
                    time.sleep(0.2)  # 稍作停顿

                    # 模拟鼠标滚轮向下滚动
                    auto.WheelDown(waitTime=0.1)  # waitTime控制滚动间隔[1](@ref)
                    library_logger.info("模拟鼠标滚轮向下滚动成功")
                else:
                    library_logger.info("文档控件边界矩形无效")
            else:
                library_logger.info("未找到指定的文档控件")
            library_logger.info("未找到可滚动容器")
            return True
        except Exception as e:
            library_logger.warning(f"滚动操作失败: {e}")
            return False
    def comment_func(self,wechat_pane)->dict:
        """
        获取单个视频详情的数据
        :return:
        """
        library_logger.info("开始获取单个视频的标题名，作者名，发布时间，分享数，转发数，喜欢数，评论数。。。。")

        # 定义需要获取的数据字段
        required_data = {
            "author_name": None,  # 作者名称
            "video_title": None,  # 视频标题
            "create_time":None, #发布时间
            "like_count": None,  # 喜欢数
            "share_count": None,  # 分享数
            "favorite_count": None,  # 点赞数
            "comment_count": None  # 评论数
        }
        # 设置超时时间（根据评论数动态调整，初始设为5分钟）

        close_zhu_button_control = auto.ButtonControl(searchFromControl=wechat_pane, Name="+关注")
        author_name_control=None
        if close_zhu_button_control.Exists():
            library_logger.info("找到了+关注按钮")
            like_control = auto.ButtonControl(searchFromControl=wechat_pane, SubName='喜欢')
            if like_control.Exists():
                library_logger.info(f"在已关注的节点中找到了包含“喜欢”的按钮: {like_control.Name}")
                required_data["like_count"] = self.like_count_func(like_control)
                required_data["share_count"] = self.share_count_func(like_control)
                required_data["favorite_count"] = self.favorite_count_func(like_control)
                required_data["comment_count"] = self.comment_count_func(like_control)
                required_data["author_name"], author_name_control = self.author_name_func(close_zhu_button_control)
        else:
            library_logger.info("未找到+关注按钮")
            like_control=auto.ButtonControl(searchFromControl=wechat_pane, SubName='喜欢')
            if like_control.Exists():
                library_logger.info(f"在未关注的节点中找到了包含“喜欢”的按钮: {like_control.Name}")
                guanzhu_control=self.yes_guanzhu_control(like_control)
                required_data["like_count"] = self.like_count_func(like_control)
                required_data["share_count"]=self.share_count_func(like_control)
                required_data["favorite_count"]=self.favorite_count_func(like_control)
                required_data["comment_count"] = self.comment_count_func(like_control)
                required_data["author_name"],author_name_control=self.author_name_func(guanzhu_control)

        video_item_title_temp=self.video_item_title_time(author_name_control)
        required_data["video_title"]=video_item_title_temp["video_title"]
        required_data["create_time"]=video_item_title_temp["create_time"]
        library_logger.info(f"结束获取单个视频的标题名，作者名，发布时间，分享数，转发数，喜欢数，评论数。。。。required_data：{required_data}")
       # time.sleep(10)
        return required_data
    def yes_guanzhu_control(self,like_control):
        """
        已关注的控件位置
        :param like_control:
        :return:
        """
        temp = like_control
        guanzhu_control=None
        found = False
        for i in range(1, 10):
            if found:
                break
            temp = temp.GetPreviousSiblingControl()
            if temp.Exists():
                #library_logger.info(f"已检查 {i} 个兄弟节点，已找到已关注的节点: {temp.Name}")
                for j in temp.GetChildren():
                    """
                    Name:	"已关注"
                    ControlType:	UIA_TextControlTypeId (0xC364)
                    LocalizedControlType:	"文本"
                    """
                    if j.Name == "已关注" and j.ControlTypeName == "TextControl":
                        library_logger.info(f"已找到已关注的节点: {j.Name}")
                        found = True
                        guanzhu_control=temp
                        break
            else:
                continue
        return guanzhu_control
    def like_count_func(self,like_control):
        """
        喜欢的数量
        :param like_control:
        :return:
        """
        favorite_count = ""
        favorite_button_sibling = like_control
        if favorite_button_sibling.Exists():
            if "喜欢" in favorite_button_sibling.Name:
                favorite_count = self.WeChat_VideoData_utils.extract_number_from_string(favorite_button_sibling.Name)
        return favorite_count
    def author_name_func(self,close_zhu_button_control):
        """
        作者名称
        :return:
        """
        temp_author_name=""
        author_name_control=None
        max_siblings_to_check = 10
        current_sibling_prev = close_zhu_button_control
        # 从“+关注”按钮或者"已关注"按钮开始，连续查找最多10个前续兄弟节点
        current_sibling_prev_status = False
        for i in range(max_siblings_to_check):
            if current_sibling_prev_status:
                library_logger.info(f"已经找到了，不需要再继续往前找前续节点了")
                break
            current_sibling_prev = current_sibling_prev.GetPreviousSiblingControl()
            if not current_sibling_prev.Exists():
                library_logger.info(f"已检查 {i + 1} 个兄弟节点，前续无更多兄弟节点")
                break
           # library_logger.info(f"正在检查第 {i + 1} 个兄弟节点: {current_sibling_prev.Name} (ControlType: {current_sibling_prev.ControlTypeName})")
            """
            作者
            1.从+关注这里往上找兄弟节点,
            -如果上个兄弟节点的孩子里面有图像UIA_ImageControlTypeId (0xC356)，则跳过这个兄弟节点，说明这是带v的官方账号,
            然后从+关注这里找上上个兄弟节点，如果上上个兄弟节点的孩子里面有UIA_TextControlTypeId (0xC364)，则就是这个兄弟节点的孩子节点的名称Name
            -如果上个兄弟节点的孩子里面有UIA_TextControlTypeId (0xC364)，则就是这个兄弟节点的孩子节点的名称Name,说明这个是普通账号
            """
            all_children = current_sibling_prev.GetChildren()
            for child_control in all_children:
                if child_control.ControlTypeName == "TextControl":  # 或者使用 child_control.ControlType == auto.ControlType.Text
                    author_name = child_control.Name
                    author_name_control = child_control
                    temp_author_name= author_name
                    #library_logger.info()(f"找到普通账号文本控件作者名称: {author_name}")
                    current_sibling_prev_status = True
                    break
                elif child_control.ControlTypeName == "ImageControl":  # 或者使用 child_control.ControlType == auto.ControlType.Image
                    library_logger.info("检测到官方账号的图像标识，继续查找...")
                    #library_logger.info()("检测到官方账号的图像标识，继续查找...")

        return temp_author_name,author_name_control
    def share_count_func(self,like_control):
        """
        分享数量
        :return:
        """
        share_count=""
        share_button_sibling = like_control.GetNextSiblingControl()
        if share_button_sibling.Exists():
            # 2. 在该兄弟节点内部查找“分享”按钮 (使用模糊匹配)
            share_button = auto.ButtonControl(searchFromControl=share_button_sibling, SubName='分享')
            if share_button.Exists(maxSearchSeconds=1):
                # 获取分享按钮的所有子控件
                all_children = share_button.GetChildren()
                # 遍历子控件，统计类型为TextControl的控件
                found_text_control = False  # 初始化一个标志变量，表示是否找到文本控件
                for child_control in all_children:
                    if child_control.ControlTypeName == "TextControl":  # 或者使用 child_control.ControlType == auto.ControlType.Text
                        library_logger.info(f"分享按钮内找到文本控件: {child_control.Name}")
                        """
                        分享
                        """
                        share_count = self.WeChat_VideoData_utils.extract_number_from_string(child_control.Name)
                        found_text_control = True
                        break
                # 如果遍历完所有子控件后仍未找到文本控件，则设置为0
                if not found_text_control:
                    library_logger.info("[DEBUG] 在分享按钮内没找到文本控件: share_count设置为0")
                    share_count= "0"
        return share_count
    def favorite_count_func(self,like_control):
        """
        点赞数量
        :return:
        """
        favorite_count=""
        favorite_button_sibling=like_control.GetNextSiblingControl().GetNextSiblingControl()
        if favorite_button_sibling.Exists():
            if "点赞" in favorite_button_sibling.Name:
                favorite_count=self.WeChat_VideoData_utils.extract_number_from_string(favorite_button_sibling.Name)
        return favorite_count
    def comment_count_func(self,like_control):
        """
        评论数量
        :return:
        """
        comment_count=""
        comment_button_sibling=like_control.GetNextSiblingControl().GetNextSiblingControl().GetNextSiblingControl()
        if comment_button_sibling.Exists():
            if "评论" in comment_button_sibling.Name:
                comment_count = self.WeChat_VideoData_utils.extract_number_from_string(comment_button_sibling.Name)
        return comment_count
    def video_item_title_time(self,author_name_control):
        """
        单个视频标题
        :return:
        """
        data={
            "video_title":"",
            "create_time":""
        }
        library_logger.info(f"开始获取视频标题和时间")
        try:
            prev_control=author_name_control.GetParentControl().GetPreviousSiblingControl().GetPreviousSiblingControl()
            #library_logger.info(f"正在检查前一个兄弟节点: {prev_control.Name} (ControlType: {prev_control.ControlTypeName})")
            if prev_control.Exists():
                all_children = prev_control.GetChildren()
                if all_children:
                    # 获取第一个子节点,通常是视频标题
                    first_child = all_children[0]
                   # library_logger.info(f"第一个子节点的名称: {first_child}")
                    first_child_children=first_child.GetChildren()
                   # library_logger.info(f"第一个子节点的子节点名称: {first_child_children}")
                    #
                    video_title=""
                    for child in first_child_children:
                        video_title+=child.Name
                    data["video_title"]=video_title
                    # 阅兵一刷高燃再刷爆哭【#九三阅兵我们为什么热泪盈眶？这就是答案】9月3日，祖国处处都是“观礼台”。屏幕前、地铁里、人海中……不约而同，人们围观、参与，共赴一个约定。\n天安门广场的观礼台上，老战士眼含热泪，庄严敬礼。老人家或许在想，牺牲的战友，若能看到今日铁流滚滚，该多欣慰。\n刘老庄连的战旗上，“庒”字多了一点。这不是错别字，而是保留了1943年旗帜上的原有字体，只为让英雄找到部队的名字。\n牌号为“1945”的阅兵车为什么是空的？不，它不是空的，它一定满载英烈，也满载我们的思念。\n有没有一个瞬间，让你突然理解“祖国”两个字的分量？也许就在这次#九三盛大阅兵，你热泪盈眶的那一刻！祝福祖国！愿万里山河永昌，祖国繁荣富强！（来源：央视新闻）\n
                    #情况1:里面有\n的看要不要去除，
                    #############################################################
                    second_child = all_children[-1]
                    first_child_children=second_child.GetChildren()
                    for child in first_child_children:
                        if child.ControlTypeName=="TextControl":
                            library_logger.info("视频发布时间",child.Name)
                            data["create_time"] = child.Name
        except Exception as e:
            library_logger.warning("单个视频标题报错",e)
        library_logger.info(f"结束获取视频标题和时间data:{data}")
        return data

    """
    单个视频评论
    """

    def is_reply_count_text_control(self,control):
        """
        判断给定的控件是否是显示'X条回复'的文本控件。
        根据你的实际观察，可能还需要检查其他属性，如ClassName或AutomationId，以提高准确性。
        """
        if control.ControlTypeName == "TextControl":  # 确保是文本控件
            if control.Name:  # 确保Name属性不为空
                # 使用正则表达式匹配数字+“条回复”的模式
                match = re.search(r'(\d+)\s*条回复', control.Name)
                if match:
                    library_logger.info(f"找到回复数量控件: {control.Name}, 共有 {match.group(1)} 条回复")
                    return True
        return False
    def video_item_comment(self,next_sibling,video_data):
        """
        获取视频评论数据，每获取一条评论就通过回调函数处理
        :param next_sibling:标签页
        :param video_data: 对应的视频数据，用于回调时关联评论和视频
        :return:
        """
        #comment_data_list=[]
        search_pinglun_text_control = self.search_pinglun_text_control_func()
        temp_control=search_pinglun_text_control
        sum_comment_count=0
        while True:
            try:
                temp_control=self.get_next_control_safe(temp_control)
                if temp_control is None:
                    library_logger.debug(f"没有更多评论了")
                    break # 没有更多控件，退出循环
                rect = temp_control.BoundingRectangle
                if (rect.left == 0 and rect.top == 0 and rect.right == 0 and rect.bottom == 0) or temp_control.IsOffscreen:
                    self.scroll_video_comment(next_sibling)
                if temp_control.Name!="":
                    required_comment_data=self.item_comment_func(temp_control)
                    library_logger.info(f"这是第{sum_comment_count+1}条评论，required_comment_data:{required_comment_data}")

                    # 通过回调函数处理单条评论数据
                    if self.comment_callback:
                        try:
                            self.comment_callback(required_comment_data, video_data)
                        except Exception as e:
                            library_logger.warning(f"评论回调函数执行失败: {e}")

                    temp_control = temp_control.GetNextSiblingControl().GetNextSiblingControl()
                    sum_comment_count += 1
                else:
                    self.find_and_click_reply_text(temp_control)
            except Exception as e:
                library_logger.warning(f"第{sum_comment_count+1}个视频获取评论内容失败：{e}")
    def get_next_control_safe(self,current_control):
        """
        安全地获取下一个兄弟控件，避免在最后一个控件时报错
        """
        try:
            next_control = current_control.GetNextSiblingControl()
            if next_control and next_control.Exists():
                return next_control
            return None
        except Exception as e:
            library_logger.warning(f"get_next_control_safe获取下一个控件时出错: {e}")
            return None
    def find_and_click_reply_text(self,parent_control, max_depth=10):
        """
        递归地从父控件开始查找所有层级的子控件，寻找并点击'X条回复'文本。
        :param parent_control: 开始查找的父控件（例如一个评论项）。
        :param max_depth: 最大搜索深度，防止无限递归。
        """
        if max_depth <= 0:
            return

        # 获取当前父控件的所有直接子控件
        children = parent_control.GetChildren()

        for child in children:
            # 检查当前子控件是否是我们要找的“条回复”文本控件
            if self.is_reply_count_text_control(child):
                try:
                    library_logger.info(f"尝试点击回复控件: {child.Name}")
                    # **尝试点击该文本控件本身**
                    child.Click(simulateMove=True)  # simulateMove 模拟鼠标移动更真实
                    time.sleep(1.5)  # **重要：点击后等待回复加载，时间可根据实际情况调整**
                    # 点击后，你可以选择跳出循环（如果确定只有一个这样的控件）
                    # break
                except Exception as e:
                    library_logger.warning(f"点击回复控件时出错: {e}")
                    # 如果直接点击文本控件无效，可以尝试查找其父控件或兄弟控件中的按钮
                    # 例如，有时“条回复”文本旁边可能有一个实际的按钮用于点击
                    parent_of_text = child.GetParentControl()
                    # 尝试在父控件中查找按钮（ButtonControl）
                    possible_button = parent_of_text.ButtonControl(searchDepth=1)
                    if possible_button.Exists():
                        try:
                            library_logger.info("尝试通过父控件中的按钮点击")
                            possible_button.Click(simulateMove=True)
                            time.sleep(1.5)
                        except Exception as btn_e:
                            library_logger.warning(f"点击按钮时出错: {btn_e}")
            else:
                # 如果当前控件不是，则递归深入其子控件继续查找
                self.find_and_click_reply_text(child, max_depth - 1)
    def item_comment_func(self,temp_control):
        """
        ""组
        -"老林主任"文本     #评论作者名
        "广东"文本         #评论地区
        "6天前"文本        #评论日期
        ""组              #评论内容
        -"有靠谱的路子"文本
        -"墙"未加标签的图片
        ""组              *评论的点赞数
        -""图像
        ""组
        -"回复"文本       *

        :param temp_control:
        :return:
        """
        required_comment_data = {
            "comment_author_name": None,  # 评论作者名称
            "comment_create_time": None,  # 评论日期
            "comment_from": None,  # 评论地区
            "comment_content": None,  # 评论内容
        }
        try:
            comment_author_name_str = ""
            comment_author_name = temp_control.GetPreviousSiblingControl().GetChildren()
            for child in comment_author_name:
                if child.ControlTypeName == "TextControl":
                    comment_author_name_str += child.Name

            content = temp_control.GetNextSiblingControl().GetNextSiblingControl().GetChildren()
            content_str = ""
            for child in content:
                if child.ControlTypeName == "TextControl":
                    content_str += child.Name

            required_comment_data["comment_from"]=temp_control.Name
            required_comment_data["comment_create_time"] = temp_control.GetNextSiblingControl().Name
            required_comment_data["comment_author_name"] =comment_author_name_str
            required_comment_data["comment_content"] = content_str
        except Exception as e:
            library_logger.warning(f"item_comment_func出错: {e}")
        return required_comment_data
    def search_pinglun_text_control_func(self):
        """
        查找评论关键字，通过这个关键字来获取评论，返回其父节点，然后通过父节点往下找获取评论
        :return:
        """
        search_pinglun_text_control = auto.TextControl(searchFromControl=self.WECHAT_PANE, Name="评论")
        if search_pinglun_text_control.Exists():
            search_pinglun_text_control = search_pinglun_text_control.GetParentControl()
            return search_pinglun_text_control
    def scroll_video_comment(self,next_sibling):
        try:
            scroll_container = auto.DocumentControl(searchDepth=8, Name=next_sibling.Name)  # 根据你的查找条件调整

            if scroll_container.Exists():
                rect = scroll_container.BoundingRectangle
                if rect.width() > 0 and rect.height() > 0:
                    # 计算文档控件的中心坐标
                    center_x = (rect.left + rect.right) // 2
                    center_y = (rect.top + rect.bottom) // 2

                    # 将鼠标移动到该中心点（确保操作焦点在目标区域）
                    auto.MoveTo(center_x, center_y)
                    time.sleep(0.2)  # 稍作停顿

                    # 模拟鼠标滚轮向下滚动
                    auto.WheelDown(waitTime=1)  # waitTime控制滚动间隔[1](@ref)
                    library_logger.info("单个视频获取评论-模拟鼠标滚轮向下滚动成功")
                else:
                    library_logger.info("单个视频获取评论-文档控件边界矩形无效")
            else:
                library_logger.info("单个视频获取评论-未找到指定的文档控件")
            library_logger.info("单个视频获取评论-未找到可滚动容器")
            return True

        except Exception as e:
            library_logger.warning(f"单个视频获取评论-滚动操作失败: {e}")
            return False
    def scroll_top(self):
        pass
    def set_comment_callback(self, callback_func):
        """
        设置评论数据回调函数

        Args:
            callback_func: 回调函数，接收单条评论数据和对应的视频数据作为参数
        """
        self.comment_callback = callback_func

class WeChatVideoCrawler:
    """
    微信视频号数据爬取管理器（ facade模式/门面模式 ）
    封装了从启动微信到获取视频数据的完整流程，简化调用。
    """

    def __init__(self):
        """初始化爬虫管理器"""
        self.automator = None  # 微信自动化器实例
        self.comment_callback = None  # 评论回调函数

    def initialize(self):
        """
        初始化微信自动化环境。
        完成所有必要的准备工作。
        """
        self.automator = WeChatAutomator()
        # 1. 打开微信，并激活
        self.automator.start_webchat()
        # 2. 查找微信窗口
        self.automator.search_wechat()
        # 3. 点击打开视频号
        self.automator.open_video_channel()
        # 4. 查找视频号窗口
        self.automator.find_video_channel()
        library_logger.info("WeChatVideoCrawler 初始化完成。")

    def set_comment_callback(self, callback_func):
        """
        设置用于处理评论数据的回调函数。

        Args:
            callback_func (function): 一个接受 comment_data 和 video_data 为参数的函数。
        """
        self.comment_callback = callback_func
        # 将回调设置给底层的 automator
        if self.automator:
            self.automator.set_comment_callback(callback_func)
        library_logger.info("评论回调函数设置成功。")

    def crawl(self, search_keyword, skip_comment=False):
        """
        执行视频号数据爬取的主要方法。

        Args:
            search_keyword (str): 要在视频号中搜索的关键字。
            skip_comment (bool): 是否跳过评论获取。默认为 False。

        Returns:
            list: 视频数据列表。
        """
        if not self.automator:
            raise RuntimeError("爬虫器未初始化，请先调用 initialize() 方法。")

        # 5. 通过视频号窗口-输入关键字并搜索
        self.automator.input_keyword_search(search_keyword)
        # 6. 等待视频列表加载完成
        status = self.automator.video_channel_lodding()

        if not status:
            library_logger.warning("视频列表加载失败。")
            return []

        # 7. 循环并自动滚动获取每个视频的数据
        library_logger.info(f"开始爬取关键词 '{search_keyword}' 的视频数据...")
        list_data = self.automator.video_list_data(skip_comment=skip_comment)

        library_logger.info(f"爬取完成！共获取到 {len(list_data)} 个视频的数据。")
        return list_data


def handle_single_comment(comment_data, video_data):
    """
    处理单条评论数据的回调函数示例
    """
    print(f"视频 '{video_data.get('video_title', '未知')}' 收到一条评论:")
    print(f"  作者: {comment_data.get('comment_author_name', '未知')}")
    print(f"  内容: {comment_data.get('comment_content', '无内容')}")
    print(f"  时间: {comment_data.get('comment_create_time', '未知')}")