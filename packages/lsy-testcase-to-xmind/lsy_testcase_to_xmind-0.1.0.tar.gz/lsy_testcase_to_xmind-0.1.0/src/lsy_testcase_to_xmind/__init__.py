from mcp.server.fastmcp import FastMCP
from typing import List, Optional
from pydantic import BaseModel
import xml.etree.ElementTree as ET
import zipfile
import os
import tempfile
import uuid
from datetime import datetime


# Create an MCP server
mcp = FastMCP("lsy-testcase-to-xmind")

class TestCaseStep(BaseModel):
    """
    测试步骤
    """
    step_number: int  # 步骤编号
    action: str  # 执行操作
    expected_result: str  # 期望结果


class TestCase(BaseModel):
    """
    单个测试用例
    """
    path: str
    name: str
    steps: List[TestCaseStep]
    priority: str  # "p0","p1","p2","p3"
    preconditions: Optional[str] = None
    remark: Optional[str] = None


class TestCaseList(BaseModel):
    """
    测试用例集
    """
    feature: str
    test_cases: List[TestCase]


def create_xmind_xml_content(test_case_list: TestCaseList):
    """
    创建XMind文件的XML内容，使用正确的XMind结构
    """
    # 创建根元素
    root = ET.Element("xmap-content", {
        "xmlns": "urn:xmind:xmap:xmlns:content:2.0",
        "xmlns:fo": "http://www.w3.org/1999/XSL/Format",
        "xmlns:svg": "http://www.w3.org/2000/svg",
        "xmlns:xhtml": "http://www.w3.org/1999/xhtml",
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
        "modified-by": "python-script",
        "timestamp": str(int(datetime.now().timestamp() * 1000)),
        "version": "2.0"
    })

    # 创建sheet
    sheet = ET.SubElement(root, "sheet", {
        "id": str(uuid.uuid4()).replace("-", "")[:24],
        "modified-by": "python-script",
        "theme": "2rrhhfcco8pl9uk8mtbfaq9ino",
        "timestamp": str(int(datetime.now().timestamp() * 1000))
    })

    # 创建根主题
    topic = ET.SubElement(sheet, "topic", {
        "id": str(uuid.uuid4()).replace("-", "")[:24],
        "modified-by": "python-script",
        "structure-class": "org.xmind.ui.map.unbalanced",
        "timestamp": str(int(datetime.now().timestamp() * 1000))
    })

    title = ET.SubElement(topic, "title")
    title.text = test_case_list.feature

    # 创建children和topics元素
    children = ET.SubElement(topic, "children")
    topics = ET.SubElement(children, "topics", {"type": "attached"})

    # 为每个测试用例创建主题
    for test_case in test_case_list.test_cases:
        # 创建测试用例主题
        case_topic = ET.SubElement(topics, "topic", {
            "id": str(uuid.uuid4()).replace("-", "")[:24],
            "modified-by": "python-script",
            "timestamp": str(int(datetime.now().timestamp() * 1000))
        })

        case_title = ET.SubElement(case_topic, "title")
        case_title.text = f"{test_case.name}"

        # 添加优先级标记
        priority_map = {"p0": "priority-1", "p1": "priority-2", "p2": "priority-3", "p3": "priority-4"}
        if test_case.priority in priority_map:
            marker_refs = ET.SubElement(case_topic, "marker-refs")
            marker_ref = ET.SubElement(marker_refs, "marker-ref")
            marker_ref.set("marker-id", priority_map[test_case.priority])

        # 创建子主题容器
        case_children = ET.SubElement(case_topic, "children")
        case_topics = ET.SubElement(case_children, "topics", {"type": "attached"})

        # 添加路径信息
        path_topic = ET.SubElement(case_topics, "topic", {
            "id": str(uuid.uuid4()).replace("-", "")[:24],
            "modified-by": "python-script",
            "timestamp": str(int(datetime.now().timestamp() * 1000))
        })
        path_title = ET.SubElement(path_topic, "title")
        path_title.text = f"路径: {test_case.path}"

        # 添加前置条件（如果有）
        if test_case.preconditions:
            preconditions_topic = ET.SubElement(case_topics, "topic", {
                "id": str(uuid.uuid4()).replace("-", "")[:24],
                "modified-by": "python-script",
                "timestamp": str(int(datetime.now().timestamp() * 1000))
            })
            preconditions_title = ET.SubElement(preconditions_topic, "title")
            preconditions_title.text = f"前置条件: {test_case.preconditions}"

        # 添加测试步骤
        steps_topic = ET.SubElement(case_topics, "topic", {
            "id": str(uuid.uuid4()).replace("-", "")[:24],
            "modified-by": "python-script",
            "timestamp": str(int(datetime.now().timestamp() * 1000))
        })
        steps_title = ET.SubElement(steps_topic, "title")
        steps_title.text = "测试步骤"

        # 创建步骤子主题容器
        steps_children = ET.SubElement(steps_topic, "children")
        steps_topics = ET.SubElement(steps_children, "topics", {"type": "attached"})

        for step in test_case.steps:
            step_topic = ET.SubElement(steps_topics, "topic", {
                "id": str(uuid.uuid4()).replace("-", "")[:24],
                "modified-by": "python-script",
                "timestamp": str(int(datetime.now().timestamp() * 1000))
            })
            step_title = ET.SubElement(step_topic, "title")
            step_title.text = f"步骤 {step.step_number}: {step.action}"

            # 创建期望结果子主题容器
            step_children = ET.SubElement(step_topic, "children")
            step_topics = ET.SubElement(step_children, "topics", {"type": "attached"})

            # 添加期望结果
            expected_result_topic = ET.SubElement(step_topics, "topic", {
                "id": str(uuid.uuid4()).replace("-", "")[:24],
                "modified-by": "python-script",
                "timestamp": str(int(datetime.now().timestamp() * 1000))
            })
            expected_result_title = ET.SubElement(expected_result_topic, "title")
            expected_result_title.text = f"期望结果: {step.expected_result}"

        # 添加备注（如果有）
        if test_case.remark:
            remark_topic = ET.SubElement(case_topics, "topic", {
                "id": str(uuid.uuid4()).replace("-", "")[:24],
                "modified-by": "python-script",
                "timestamp": str(int(datetime.now().timestamp() * 1000))
            })
            remark_title = ET.SubElement(remark_topic, "title")
            remark_title.text = f"备注: {test_case.remark}"

    # 添加扩展信息
    extensions = ET.SubElement(topic, "extensions")
    extension = ET.SubElement(extensions, "extension", {"provider": "org.xmind.ui.map.unbalanced"})
    content = ET.SubElement(extension, "content")
    right_number = ET.SubElement(content, "right-number")
    right_number.text = "1"

    # 添加sheet标题
    sheet_title = ET.SubElement(sheet, "title")
    sheet_title.text = "画布 1"

    # 转换为XML字符串
    tree = ET.ElementTree(root)

    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml', encoding='utf-8') as f:
        # 添加XML声明
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
        tree.write(f, encoding='unicode', xml_declaration=False)
        return f.name


def create_xmind_manifest():
    """
    创建XMind清单文件
    """
    root = ET.Element("manifest", {
        "xmlns": "urn:xmind:xmap:xmlns:manifest:1.0"
    })

    # 添加文件条目
    file_entry = ET.SubElement(root, "file-entry", {
        "full-path": "content.xml",
        "media-type": "text/xml"
    })

    file_entry = ET.SubElement(root, "file-entry", {
        "full-path": "META-INF/",
        "media-type": ""
    })

    file_entry = ET.SubElement(root, "file-entry", {
        "full-path": "META-INF/manifest.xml",
        "media-type": "text/xml"
    })

    file_entry = ET.SubElement(root, "file-entry", {
        "full-path": "Thumbnails/",
        "media-type": ""
    })

    file_entry = ET.SubElement(root, "file-entry", {
        "full-path": "Thumbnails/thumbnail.png",
        "media-type": "image/png"
    })

    # 转换为XML字符串
    tree = ET.ElementTree(root)

    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml', encoding='utf-8') as f:
        # 添加XML声明
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
        tree.write(f, encoding='unicode', xml_declaration=False)
        return f.name

@mcp.tool()
def create_xmind_with_xml(test_case_list: TestCaseList, output_path: str="测试用例.xmind") -> str:
    """
    使用test_case_list生成xmind文件，文件路径为output_path
    """
    try:
        output_path=test_case_list.feature+output_path
        # 确保输出目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # 创建内容XML
        content_file = create_xmind_xml_content(test_case_list)

        # 创建清单XML
        manifest_file = create_xmind_manifest()

        # 创建XMind文件（ZIP格式）
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as xmind_file:
            # 添加内容文件
            xmind_file.write(content_file, "content.xml")

            # 添加清单文件
            os.makedirs("META-INF", exist_ok=True)
            xmind_file.write(manifest_file, "META-INF/manifest.xml")

        # 清理临时文件
        os.unlink(content_file)
        os.unlink(manifest_file)

        return True

    except Exception as e:
        # 清理临时文件
        if 'content_file' in locals() and os.path.exists(content_file):
            os.unlink(content_file)
        if 'manifest_file' in locals() and os.path.exists(manifest_file):
            os.unlink(manifest_file)
        return False


def main() -> None:
    # 启动MCP服务，使用标准输入输出作为传输方式
    mcp.run(transport='stdio')
