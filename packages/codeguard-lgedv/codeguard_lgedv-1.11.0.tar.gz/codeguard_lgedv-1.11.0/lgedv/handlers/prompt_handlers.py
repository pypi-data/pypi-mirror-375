"""
Prompt handlers for MCP server operations
Xử lý các MCP prompts cho phân tích code
"""
import os
from typing import Dict
from mcp import types
from lgedv.prompts.prompt_templates import PromptTemplates
from lgedv.analyzers.memory_analyzer import MemoryAnalyzer
from lgedv.modules.config import get_src_dir, setup_logging

logger = setup_logging()

class PromptHandler:
    """Handler cho các MCP prompts"""
    
    def __init__(self):
        self.templates = PromptTemplates()
    
   

    async def handle_prompt(self, name: str, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """
        Route và xử lý prompt calls
        
        Args:
            name: Tên prompt
            arguments: Arguments cho prompt
            
        Returns:
            GetPromptResult
        """
        logger.info(f"Prompt called: {name} with arguments: {arguments}")
        
        try:
            if name == "check_lgedv":
                return await self._handle_lgedv_check()
            elif name == "check_static_analysis":
                return await self._handle_lge_static_check()
            elif name == "check_misra_cpp":
                return await self._handle_misra_cpp_check()
            elif name == "check_autosar":  
                return await self._handle_autosar_check()
            elif name == "check_misra_c":  
                return await self._handle_misra_c_check()
            elif name == "check_certcpp":
                return await self._handle_certcpp_check()
            elif name == "check_custom":
                return await self._handle_custom_check()
            elif name == "check_cim_static":
                return await self._handle_cim_static_check()
            elif name == "check_cim_misra_cpp":
                return await self._handle_cim_misra_cpp_check()
            elif name == "check_races":
                return await self._handle_race_condition_analysis(arguments)
            elif name == "check_leaks":
                return await self._handle_memory_leak_analysis(arguments)
            elif name == "check_resources":
                return await self._handle_resource_leak_analysis(arguments)
            elif name == "get_code_context":
                return await self._handle_code_context()  
            elif name == "reset_analysis":
                return await self._handle_reset_analysis_prompt(arguments)
            if name == "reset_mem_check":
                return await self._handle_reset_mem_check_prompt(arguments)
            if name == "reset_resource_check":
                return await self._handle_reset_resource_check_prompt(arguments)
            if name == "reset_race_check":
                return await self._handle_reset_race_check_prompt(arguments)
            elif name == "check_design":
                return await self._handle_design_check(arguments)
            else:
                raise ValueError(f"Unknown prompt: {name}")
                
        except Exception as e:
            logger.exception(f"Error in prompt handler for {name}: {e}")
            raise
    
    async def _handle_lgedv_check(self) -> types.GetPromptResult:
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++. Hãy phân tích file hiện tại để phát hiện vi phạm các quy tắc LGEDV cho phần mềm ô tô.\n"
                "Nếu chưa có file rule, hãy gọi fetch_lgedv_rule từ MCP server.\n"
                "Luôn sử dụng bộ quy tắc LGEDV mới nhất vừa fetch để phân tích, không dùng rule cũ hoặc built-in.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Tìm TẤT CẢ vi phạm quy tắc trên\n"
                "- Tập trung vào vi phạm LGEDV\n"
                "- Ghi rõ số hiệu rule (VD: LGEDV_CRCL_0001, MISRA Rule 8-4-3, DCL50-CPP, RS-001)\n"
                "- Kiểm tra mọi dòng code, kể cả unreachable, dead code, return sớm, magic number\n"
                "- Kiểm tra mọi điểm acquire/release resource, mọi exit point, mọi function/method\n"
                "- Đưa ra code fix cụ thể cho từng lỗi\n"
                "- Ghi số dòng code gốc trong báo cáo\n\n"                
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi lỗi:\n"
                "## 🚨 Vấn đề [#]: [Mô tả ngắn]\n\n"
                "**Rule vi phạm:** [SỐ HIỆU] - [Mô tả rule]\n\n"
                "**Vị trí:** [tên hàm hoặc global/unknown]\n\n"
                "**Mức độ:** [Critical/High/Medium/Low]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[code lỗi]\n```\n"
                "**Code đã sửa:**\n"
                "```cpp\n[code đúng]\n```\n"
                "**Giải thích:** [Vì sao vi phạm và cách sửa]\n\n"             
                "**Lưu ý:** Nếu cần toàn bộ file code đã fix, hãy yêu cầu rõ ràng."
            )
        else:
            prompt = self.templates.get_lgedv_analysis_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for LGEDV rule on current file.",
        )
        logger.info("LGEDV check prompt completed")
        return result
    
    async def _handle_lge_static_check(self) -> types.GetPromptResult:
        """Handle LGE Static Analysis code checking prompt"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++. Hãy phân tích file hiện tại để phát hiện vi phạm các quy tắc LGE Static Analysis.\n"
                "Nếu chưa có file rule, hãy gọi fetch_static_analysis_rule từ MCP server.\n"
                "Luôn sử dụng bộ quy tắc LGE Static Analysis mới nhất vừa fetch để phân tích, không dùng rule cũ hoặc built-in.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Tìm TẤT CẢ vi phạm quy tắc trên\n"
                "- Tập trung vào vi phạm LGE Static Analysis\n"
                "- Ghi rõ số hiệu rule (VD: ARRAY_VS_SINGLETON, ATOMICITY, BAD_ALLOC_ARITHMETIC, v.v.)\n"
                "- Kiểm tra mọi dòng code, kể cả unreachable, dead code, return sớm, magic number\n"
                "- Kiểm tra mọi điểm acquire/release resource, mọi exit point, mọi function/method\n"
                "- Đưa ra code fix cụ thể cho từng lỗi\n"
                "- Ghi số dòng code gốc trong báo cáo\n\n"
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi lỗi:\n"
                "## 🚨 Vấn đề [#]: [Mô tả ngắn]\n\n"
                "**Rule vi phạm:** [SỐ HIỆU] - [Mô tả rule]\n\n"
                "**Vị trí:** [tên hàm hoặc global/unknown]\n\n"
                "**Mức độ:** [Critical/High/Medium/Low]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[code lỗi]\n```\n"
                "**Code đã sửa:**\n"
                "```cpp\n[code đúng]\n```\n"
                "**Giải thích:** [Vì sao vi phạm và cách sửa]\n\n"
                "**Lưu ý:** Nếu cần toàn bộ file code đã fix, hãy yêu cầu rõ ràng."
            )
        else:
            prompt = self.templates.get_lge_static_analysis_prompt()  # Cần thêm template này
        
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for LGE Static Analysis rule on current file.",
        )
        logger.info("LGE Static Analysis check prompt completed")
        return result

    async def _handle_misra_cpp_check(self) -> types.GetPromptResult:
        """Handle MISRA code checking prompt"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++. Hãy phân tích file hiện tại để phát hiện vi phạm các quy tắc MISRA C++ 2008 cho phần mềm an toàn.\n"
                "Nếu chưa có file rule, hãy gọi fetch_misra_cpp_rule từ MCP server.\n"
                "Luôn sử dụng bộ quy tắc MISRA mới nhất vừa fetch để phân tích, không dùng rule cũ hoặc built-in.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Tìm TẤT CẢ vi phạm quy tắc trên\n"
                "- Tập trung vào vi phạm MISRA\n"
                "- Ghi rõ số hiệu rule (VD: MISRA Rule 8-4-3, LGEDV_CRCL_0001, DCL50-CPP, RS-001)\n"
                "- Kiểm tra mọi dòng code, kể cả unreachable, dead code, return sớm, magic number\n"
                "- Kiểm tra mọi điểm acquire/release resource, mọi exit point, mọi function/method\n"
                "- Đưa ra code fix cụ thể cho từng lỗi\n"
                "- Ghi số dòng code gốc trong báo cáo\n\n"
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi lỗi:\n"
                "## 🚨 Vấn đề [#]: [Mô tả ngắn]\n\n"
                "**Rule vi phạm:** [SỐ HIỆU] - [Mô tả rule]\n\n"
                "**Vị trí:** [tên hàm hoặc global/unknown]\n\n"
                "**Mức độ:** [Critical/High/Medium/Low]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[code lỗi]\n```\n"
                "**Code đã sửa:**\n"
                "```cpp\n[code đúng]\n```\n"
                "**Giải thích:** [Vì sao vi phạm và cách sửa]\n\n"
                "**Lưu ý:** Nếu cần toàn bộ file code đã fix, hãy yêu cầu rõ ràng."
            )
        else:
            prompt = self.templates.get_misra_analysis_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for MISRA rule on current file.",
        )
        logger.info("MISRA check prompt completed")
        return result
    
    async def _handle_certcpp_check(self) -> types.GetPromptResult:
        """Handle CERT C++ code checking prompt"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++. Hãy phân tích file hiện tại để phát hiện vi phạm các quy tắc CERT C++ Secure Coding Standard.\n"
                "Nếu chưa có file rule, hãy gọi fetch_certcpp_rule từ MCP server.\n"
                "Luôn sử dụng bộ quy tắc CERT C++ mới nhất vừa fetch để phân tích, không dùng rule cũ hoặc built-in.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Tìm TẤT CẢ vi phạm quy tắc trên\n"
                "- Tập trung vào vi phạm CERT\n"
                "- Ghi rõ số hiệu rule (VD: DCL50-CPP, MISRA Rule 8-4-3, LGEDV_CRCL_0001, RS-001)\n"
                "- Kiểm tra mọi dòng code, kể cả unreachable, dead code, return sớm, magic number\n"
                "- Kiểm tra mọi điểm acquire/release resource, mọi exit point, mọi function/method\n"
                "- Đưa ra code fix cụ thể cho từng lỗi\n"
                "- Ghi số dòng code gốc trong báo cáo\n\n"
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi lỗi:\n"
                "## 🚨 Vấn đề [#]: [Mô tả ngắn]\n\n"
                "**Rule vi phạm:** [SỐ HIỆU] - [Mô tả rule]\n\n"
                "**Vị trí:** [tên hàm hoặc global/unknown]\n\n"
                "**Mức độ:** [Critical/High/Medium/Low]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[code lỗi]\n```\n"
                "**Code đã sửa:**\n"
                "```cpp\n[code đúng]\n```\n"
                "**Giải thích:** [Vì sao vi phạm và cách sửa]\n\n"               
                "**Lưu ý:** Nếu cần toàn bộ file code đã fix, hãy yêu cầu rõ ràng."
            )
        else:
            prompt = self.templates.get_certcpp_analysis_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for CERT C++ rule on current file.",
        )
        logger.info("CERT C++ check prompt completed")
        return result
    
    async def _handle_custom_check(self) -> types.GetPromptResult:
        """Handle Custom rule checking prompt"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++. Hãy phân tích file hiện tại để phát hiện vi phạm các quy tắc custom dưới đây.\n"
                "Nếu chưa có file rule, hãy gọi fetch_custom_rule từ MCP server.\n"
                "Luôn sử dụng bộ quy tắc custom mới nhất vừa fetch để phân tích, không dùng rule cũ hoặc built-in.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Tìm TẤT CẢ vi phạm quy tắc trên\n"
                "- Tập trung vào vi phạm custom rule\n"
                "- Ghi rõ số hiệu rule (VD: CUSTOM-001, MISRA Rule 8-4-3, LGEDV_CRCL_0001, RS-001)\n"
                "- Kiểm tra mọi dòng code, kể cả unreachable, dead code, return sớm, magic number\n"
                "- Kiểm tra mọi điểm acquire/release resource, mọi exit point, mọi function/method\n"
                "- Đưa ra code fix cụ thể cho từng lỗi\n"
                "- Ghi số dòng code gốc trong báo cáo\n\n"
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi lỗi:\n"
                "## 🚨 Vấn đề [#]: [Mô tả ngắn]\n\n"
                "**Rule vi phạm:** [SỐ HIỆU] - [Mô tả rule]\n\n"
                "**Vị trí:** [tên hàm hoặc global/unknown]\n\n"
                "**Mức độ:** [Critical/High/Medium/Low]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[code lỗi]\n```\n"
                "**Code đã sửa:**\n"
                "```cpp\n[code đúng]\n```\n"
                "**Giải thích:** [Vì sao vi phạm và cách sửa]\n\n"         
                "**Lưu ý:** Nếu cần toàn bộ file code đã fix, hãy yêu cầu rõ ràng."
            )
        else:
            prompt = self.templates.get_custom_analysis_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for Custom rule on current file.",
        )
        logger.info("Custom check prompt completed")
        return result
    
   
    async def _handle_cim_static_check(self) -> types.GetPromptResult:
        """Handle CIM Static Analysis (Coverity) result verification prompt"""
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++/C với kinh nghiệm sâu về Coverity Static Analysis. "
                "Hãy phân tích file code hiện tại cùng với các báo cáo vi phạm từ hệ thống CIM (Coverity).\n"
                "Nếu chưa có file rule, hãy gọi fetch_static_analysis_rule từ MCP server để tải bộ quy tắc LGE Static Analysis.\n"
                "Luôn sử dụng bộ quy tắc mới nhất vừa fetch để đối chiếu với kết quả CIM.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                
                "**NHIỆM VỤ CHÍNH:**\n"
                "1. **KIỂM TRA TÍNH CHÍNH XÁC**: Xác minh xem các CID (Coverity Issue ID) được báo cáo có thực sự là lỗi hay không\n"
                "2. **ĐỀ XUẤT GIẢI PHÁP**: Đưa ra code fix cụ thể cho mỗi lỗi thực sự\n"
                "3. **ĐỐI CHIẾU RULE**: So sánh với bộ quy tắc LGE Static Analysis để xác thực\n\n"
                
                "**PHÂN TÍCH CID FORMAT:**\n"
                "- CID [số]: [loại lỗi] - [mô tả chi tiết]\n"
                "- Ví dụ: CID 6863827: Variable copied when it could be moved (COPY_INSTEAD_OF_MOVE)\n"
                "- Ví dụ: CID 7257883: Unchecked return value (CHECKED_RETURN)\n"
                "- Các loại phổ biến: CHECKED_RETURN, COPY_INSTEAD_OF_MOVE, NULL_RETURNS, RESOURCE_LEAK, TAINTED_DATA\n\n"
                
                "**LƯU Ý QUAN TRỌNG VỀ CID SELECTION:**\n"
                "- **CHỈ PHÂN TÍCH CID CÓ MÔ TẢ CHI TIẾT**: Chỉ focus vào những CID có mô tả defect cụ thể\n"
                "- **BỎ QUA CID 'SELECT ISSUE'**: Không phân tích những CID chỉ có [ \"select issue\" ] mà không có mô tả chi tiết\n"
                "- **Ví dụ CID cần phân tích**: CID 6863827: Variable copied when it could be moved (COPY_INSTEAD_OF_MOVE) - detailed description here...\n"
                "- **Ví dụ CID bỏ qua**: CID 6795225: [ \"select issue\" ]\n\n"
                
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Đọc kỹ từng CID CÓ MÔ TẢ CHI TIẾT và vị trí line number được báo\n"
                "- Kiểm tra context xung quanh để hiểu flow execution\n"
                "- Xác định: TRUE POSITIVE (lỗi thực) vs FALSE POSITIVE (báo nhầm)\n"
                "- Đánh giá mức độ nghiêm trọng: Critical/High/Medium/Low/Info\n"
                "- Kiểm tra các pattern: memory leaks, null pointer, buffer overflow, race conditions, resource leaks\n"      
                "- Đối chiếu với bộ quy tắc LGE Static Analysis để xác thực độ chính xác\n"
                "- **IGNORE tất cả CID chỉ có [ \"select issue\" ] mà không có mô tả defect cụ thể**\n\n"
                
                "**ĐỊNH DẠNG BÁO CÁO:**\n"
                "Với mỗi CID CÓ MÔ TẢ CHI TIẾT:\n"
                "## 🔍 CID [số]: [Tên lỗi]\n\n"
                "**Vị trí:** Line [số] trong [tên hàm hoặc global scope]\n\n"
                "**Loại phân tích:** [TRUE POSITIVE/FALSE POSITIVE]\n\n"
                "**Mức độ nghiêm trọng:** [Critical/High/Medium/Low/Info]\n\n"
                "**Mô tả lỗi:** [Giải thích chi tiết vấn đề Coverity phát hiện]\n\n"
                "**Đối chiếu rule:** [So sánh với LGE Static Analysis rules]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[paste exact code có lỗi với line numbers]\n```\n\n"
                
                "**Code đã sửa:** (chỉ cho TRUE POSITIVE)\n"
                "```cpp\n[code đã fix hoàn chỉnh]\n```\n\n"
                
                "**Giải thích fix:** [Tại sao fix này đúng, an toàn và hiệu quả hơn]\n\n"              
                "**Ghi chú:** [Context hoặc lưu ý đặc biệt, impact đến performance]\n\n"
                "---\n\n"
                
                "**TỔNG KẾT CUỐI BÁO CÁO:**\n"
                "- Tổng số CID CÓ MÔ TẢ CHI TIẾT phát hiện: [X]\n"
                "- CID chỉ có [ \"select issue\" ] đã bỏ qua: [Y]\n"
                "- TRUE POSITIVE (cần fix ngay): [Z]\n"
                "- FALSE POSITIVE (có thể ignore): [W]\n"
                "- Critical/High priority: [V] (ưu tiên cao nhất)\n"         
                "- Phù hợp với LGE Static Analysis: [L] (đối chiếu với bộ rule)\n\n"
                
                "**KHUYẾN NGHỊ HÀNH ĐỘNG:**\n"
                "1. Fix ngay các Critical/High severity issues có mô tả chi tiết\n"
                "2. Review và plan cho Medium severity\n"
                "3. Suppress FALSE POSITIVE với comment rõ ràng\n"
                "4. Update coding practices để tránh tương lai\n"
                "5. Có thể review lại những CID [ \"select issue\" ] nếu cần thiết\n\n"
                
                "**LƯU Ý QUAN TRỌNG:**\n"
                "- **CHỈ PHÂN TÍCH CID CÓ MÔ TẢ DEFECT CỤ THỂ** - bỏ qua [ \"select issue\" ]\n"
                "- Ưu tiên phân tích security và memory safety defects\n"
                "- Với FALSE POSITIVE, giải thích rõ tại sao Coverity báo nhầm\n"
                "- Đề xuất suppression comment nếu cần: // coverity[CID_NUMBER]\n"
                "- Kiểm tra cross-reference giữa các CID liên quan\n"
                "- Xem xét impact performance của fix\n"
                "- Đảm bảo fix không gây side effects khác\n"
                "- Luôn đối chiếu với bộ quy tắc LGE Static Analysis để đảm bảo consistency"
            )
        else:
            prompt = (
                "You are a C++/C static analysis expert with deep Coverity Static Analysis experience. "
                "Please analyze the current code file along with CIM (Coverity) violation reports.\n"
                "If no rule file available, call fetch_static_analysis_rule from MCP server to download LGE Static Analysis rules.\n"
                "Always use the latest fetched rules to cross-reference with CIM results.\n"
                "Please specify which rule set you are using in your report.\n\n"
                
                "**PRIMARY TASKS:**\n"
                "1. **ACCURACY VERIFICATION**: Verify if reported CIDs (Coverity Issue IDs) are actual defects\n"
                "2. **SOLUTION PROPOSAL**: Provide specific code fixes for each real defect\n"
                "3. **RULE CROSS-REFERENCE**: Compare with LGE Static Analysis rules for validation\n\n"
                
                "**CID FORMAT ANALYSIS:**\n"
                "- CID [number]: [defect type] - [detailed description]\n"
                "- Example: CID 6863827: Variable copied when it could be moved (COPY_INSTEAD_OF_MOVE)\n"
                "- Example: CID 7257883: Unchecked return value (CHECKED_RETURN)\n"
                "- Common types: CHECKED_RETURN, COPY_INSTEAD_OF_MOVE, NULL_RETURNS, RESOURCE_LEAK, TAINTED_DATA\n\n"
                
                "**IMPORTANT NOTE ABOUT CID SELECTION:**\n"
                "- **ANALYZE ONLY CIDs WITH DETAILED DESCRIPTIONS**: Focus only on CIDs with specific defect descriptions\n"
                "- **IGNORE 'SELECT ISSUE' CIDs**: Skip CIDs that only have [ \"select issue\" ] without detailed description\n"
                "- **Example CID to analyze**: CID 6863827: Variable copied when it could be moved (COPY_INSTEAD_OF_MOVE) - detailed description here...\n"
                "- **Example CID to ignore**: CID 6795225: [ \"select issue\" ]\n\n"
                
                "**ANALYSIS REQUIREMENTS:**\n"
                "- Read each CID WITH DETAILED DESCRIPTION and reported line number carefully\n"
                "- Check surrounding context to understand execution flow\n"
                "- Determine: TRUE POSITIVE (real defect) vs FALSE POSITIVE (false alarm)\n"
                "- Assess severity: Critical/High/Medium/Low/Info\n"
                "- Check patterns: memory leaks, null pointer, buffer overflow, race conditions, resource leaks\n"            
                "- Cross-reference with LGE Static Analysis rules for validation\n"
                "- **IGNORE all CIDs with only [ \"select issue\" ] and no specific defect description**\n\n"
                
                "**REPORT FORMAT:**\n"
                "For each CID WITH DETAILED DESCRIPTION:\n"
                "## 🔍 CID [number]: [Defect Name]\n\n"
                "**Location:** Line [number] in [function name or global scope]\n\n"
                "**Analysis Type:** [TRUE POSITIVE/FALSE POSITIVE]\n\n"
                "**Severity:** [Critical/High/Medium/Low/Info]\n\n"
                "**Defect Description:** [Detailed explanation of what Coverity detected]\n\n"
                "**Rule Cross-Reference:** [Compare with LGE Static Analysis rules]\n\n"
                "**Current Code:**\n"
                "```cpp\n[paste exact defective code with line numbers]\n```\n\n"
                
                "**Fixed Code:** (only for TRUE POSITIVE)\n"
                "```cpp\n[complete fixed code]\n```\n\n"
                
                "**Fix Explanation:** [Why this fix is correct, safe and more efficient]\n\n"            
                "**Notes:** [Context or special considerations, performance impact]\n\n"
                "---\n\n"
                
                "**FINAL SUMMARY:**\n"
                "- Total CIDs WITH DETAILED DESCRIPTION detected: [X]\n"
                "- CIDs with only [ \"select issue\" ] ignored: [Y]\n"
                "- TRUE POSITIVE (needs immediate fix): [Z]\n"
                "- FALSE POSITIVE (can be ignored): [W]\n"
                "- Critical/High priority: [V] (highest priority)\n"                
                "- LGE Static Analysis compliance: [L] (rule set cross-reference)\n\n"
                
                "**ACTION RECOMMENDATIONS:**\n"
                "1. Fix Critical/High severity issues with detailed descriptions immediately\n"
                "2. Review and plan for Medium severity\n"
                "3. Suppress FALSE POSITIVE with clear comments\n"
                "4. Update coding practices for future prevention\n"
                "5. May review [ \"select issue\" ] CIDs separately if needed\n\n"
                
                "**IMPORTANT NOTES:**\n"
                "- **ANALYZE ONLY CIDs WITH SPECIFIC DEFECT DESCRIPTIONS** - ignore [ \"select issue\" ]\n"
                "- Prioritize security and memory safety defects\n"
                "- For FALSE POSITIVE, explain clearly why Coverity reported incorrectly\n"
                "- Suggest suppression comments if needed: // coverity[CID_NUMBER]\n"
                "- Check cross-references between related CIDs\n"
                "- Consider performance impact of fixes\n"
                "- Ensure fixes don't cause other side effects\n"
                "- Always cross-reference with LGE Static Analysis rules for consistency"
            )
        
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for CIM Static Analysis (Coverity) result verification with LGE rule cross-reference.",
        )
        logger.info("CIM Static Analysis check prompt")
        return result
    
    
    async def _handle_cim_misra_cpp_check(self) -> types.GetPromptResult:
        """Handle CIM Static Analysis (Coverity) result verification prompt for MISRA C++ violations"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++/C với kinh nghiệm sâu về Coverity Static Analysis và MISRA C++ 2008. "
                "Hãy phân tích file code hiện tại cùng với các báo cáo vi phạm MISRA C++ từ hệ thống CIM (Coverity).\n"
                "Nếu chưa có file rule, hãy gọi fetch_misra_cpp_rule từ MCP server để tải bộ quy tắc MISRA C++ 2008.\n"
                "Luôn sử dụng bộ quy tắc MISRA C++ mới nhất vừa fetch để đối chiếu với kết quả CIM.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                
                "**NHIỆM VỤ CHÍNH:**\n"
                "1. **KIỂM TRA TÍNH CHÍNH XÁC**: Xác minh xem các CID (Coverity Issue ID) cho MISRA C++ có thực sự là vi phạm hay không\n"
                "2. **ĐỀ XUẤT GIẢI PHÁP**: Đưa ra code fix cụ thể cho mỗi vi phạm MISRA C++ thực sự\n"
                "3. **ĐỐI CHIẾU RULE**: So sánh với bộ quy tắc MISRA C++ 2008 để xác thực\n\n"
                
                "**PHÂN TÍCH CID FORMAT CHO MISRA C++:**\n"
                "- CID [số]: MISRA C++-2008 [Category] (MISRA C++-2008 Rule [X-Y-Z])\n"
                "- Ví dụ: CID 6237279: MISRA C++-2008 Basic Concepts (MISRA C++-2008 Rule 3-2-3)\n"
                "- Ví dụ: CID 6244494: MISRA C++-2008 Basic Concepts (MISRA C++-2008 Rule 3-9-2)\n"
                "- Các category phổ biến: Basic Concepts, Lexical Conventions, Declarations, Preprocessor Directives\n\n"
                
                "**LƯU Ý QUAN TRỌNG VỀ CID SELECTION:**\n"
                "- **CHỈ PHÂN TÍCH CID CÓ MÔ TẢ CHI TIẾT**: Chỉ focus vào những CID có mô tả violation cụ thể\n"
                "- **BỎ QUA CID 'SELECT ISSUE'**: Không phân tích những CID chỉ có [ \"select issue\" ] mà không có mô tả chi tiết\n"
                "- **Ví dụ CID cần phân tích**: CID 6769436: (#1 of 1): MISRA C++-2008 Declarations (MISRA C++-2008 Rule 7-1-1) misra_cpp_2008_rule_7_1_1_violation: The variable strValZ has a non-const type...\n"
                "- **Ví dụ CID bỏ qua**: CID 6795225:MISRA C++-2008 Declarations (MISRA C++-2008 Rule 7-1-1) [ \"select issue\" ]\n\n"
                
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Đọc kỹ từng CID MISRA C++ CÓ MÔ TẢ CHI TIẾT và vị trí line number được báo\n"
                "- Kiểm tra context xung quanh để hiểu vi phạm rule cụ thể\n"
                "- Xác định: TRUE POSITIVE (vi phạm thực) vs FALSE POSITIVE (báo nhầm)\n"
                "- Đánh giá mức độ nghiêm trọng: Critical/High/Medium/Low/Info\n"
                "- Tập trung vào compliance với MISRA C++ 2008 standard\n"      
                "- Đối chiếu với bộ quy tắc MISRA C++ 2008 chính thức để xác thực\n"
                "- **IGNORE tất cả CID chỉ có [ \"select issue\" ] mà không có mô tả violation cụ thể**\n\n"
                
                "**ĐỊNH DẠNG BÁO CÁO:**\n"
                "Với mỗi CID MISRA C++ CÓ MÔ TẢ CHI TIẾT:\n"
                "## 🔍 CID [số]: MISRA C++ Rule [X-Y-Z] Violation\n\n"
                "**Vị trí:** Line [số] trong [tên hàm hoặc global scope]\n\n"
                "**Rule vi phạm:** MISRA C++-2008 Rule [X-Y-Z] - [Mô tả rule từ standard]\n\n"
                "**Loại phân tích:** [TRUE POSITIVE/FALSE POSITIVE]\n\n"
                "**Mức độ nghiêm trọng:** [Critical/High/Medium/Low/Info]\n\n"
                "**Mô tả vi phạm:** [Giải thích chi tiết vi phạm MISRA rule cụ thể]\n\n"
                "**Đối chiếu MISRA rule:** [So sánh với MISRA C++ 2008 standard chính thức]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[paste exact code vi phạm với line numbers]\n```\n\n"
                
                "**Code đã sửa:** (chỉ cho TRUE POSITIVE)\n"
                "```cpp\n[code đã fix tuân thủ MISRA C++]\n```\n\n"
                
                "**Giải thích fix:** [Tại sao fix này tuân thủ MISRA C++ và an toàn hơn]\n\n"              
                "**Ghi chú:** [Context đặc biệt, deviation có thể chấp nhận được]\n\n"
                "---\n\n"
                
                "**TỔNG KẾT CUỐI BÁO CÁO:**\n"
                "- Tổng số CID MISRA C++ CÓ MÔ TẢ CHI TIẾT phát hiện: [X]\n"
                "- CID chỉ có [ \"select issue\" ] đã bỏ qua: [Y]\n"
                "- TRUE POSITIVE (cần fix ngay): [Z]\n"
                "- FALSE POSITIVE (có thể ignore): [W]\n"
                "- Critical/High priority: [V] (ưu tiên cao nhất)\n"         
                "- Tuân thủ MISRA C++ 2008: [M] (đối chiếu với standard)\n\n"
                
                "**KHUYẾN NGHỊ HÀNH ĐỘNG:**\n"
                "1. Fix ngay các Critical/High severity MISRA violations có mô tả chi tiết\n"
                "2. Document justified deviations với clear rationale\n"
                "3. Suppress FALSE POSITIVE với MISRA deviation comments\n"
                "4. Update coding guidelines để prevent future violations\n"
                "5. Có thể review lại những CID [ \"select issue\" ] nếu cần thiết\n\n"
                
                "**LƯU Ý QUAN TRỌNG:**\n"
                "- **CHỈ PHÂN TÍCH CID CÓ MÔ TẢ VIOLATION CỤ THỂ** - bỏ qua [ \"select issue\" ]\n"
                "- Ưu tiên các MISRA rules liên quan đến safety và reliability\n"
                "- Với FALSE POSITIVE, giải thích rõ tại sao rule không áp dụng\n"
                "- Đề xuất MISRA deviation comments: /* MISRA C++ Rule X-Y-Z deviation: [reason] */\n"
                "- Kiểm tra consistency với toàn bộ MISRA C++ compliance strategy\n"
                "- Xem xét impact của fix đến overall code maintainability\n"
                "- Đảm bảo fix không vi phạm rules khác\n"
                "- Luôn đối chiếu với MISRA C++ 2008 standard chính thức"
            )
        else:
            prompt = (
                "You are a C++/C static analysis expert with deep Coverity Static Analysis and MISRA C++ 2008 experience. "
                "Please analyze the current code file along with CIM (Coverity) MISRA C++ violation reports.\n"
                "If no rule file available, call fetch_misra_cpp_rule from MCP server to download MISRA C++ 2008 rules.\n"
                "Always use the latest fetched MISRA C++ rules to cross-reference with CIM results.\n"
                "Please specify which rule set you are using in your report.\n\n"
                
                "**PRIMARY TASKS:**\n"
                "1. **ACCURACY VERIFICATION**: Verify if reported CIDs (Coverity Issue IDs) for MISRA C++ are actual violations\n"
                "2. **SOLUTION PROPOSAL**: Provide specific code fixes for each real MISRA C++ violation\n"
                "3. **RULE CROSS-REFERENCE**: Compare with MISRA C++ 2008 rules for validation\n\n"
                
                "**CID FORMAT ANALYSIS FOR MISRA C++:**\n"
                "- CID [number]: MISRA C++-2008 [Category] (MISRA C++-2008 Rule [X-Y-Z])\n"
                "- Example: CID 6237279: MISRA C++-2008 Basic Concepts (MISRA C++-2008 Rule 3-2-3)\n"
                "- Example: CID 6244494: MISRA C++-2008 Basic Concepts (MISRA C++-2008 Rule 3-9-2)\n"
                "- Common categories: Basic Concepts, Lexical Conventions, Declarations, Preprocessor Directives\n\n"
                
                "**IMPORTANT NOTE ABOUT CID SELECTION:**\n"
                "- **ANALYZE ONLY CIDs WITH DETAILED DESCRIPTIONS**: Focus only on CIDs with specific violation descriptions\n"
                "- **IGNORE 'SELECT ISSUE' CIDs**: Skip CIDs that only have [ \"select issue\" ] without detailed description\n"
                "- **Example CID to analyze**: CID 6769436: (#1 of 1): MISRA C++-2008 Declarations (MISRA C++-2008 Rule 7-1-1) misra_cpp_2008_rule_7_1_1_violation: The variable strValZ has a non-const type...\n"
                "- **Example CID to ignore**: CID 6795225:MISRA C++-2008 Declarations (MISRA C++-2008 Rule 7-1-1) [ \"select issue\" ]\n\n"
                
                "**ANALYSIS REQUIREMENTS:**\n"
                "- Read each MISRA C++ CID WITH DETAILED DESCRIPTION and reported line number carefully\n"
                "- Check surrounding context to understand specific rule violation\n"
                "- Determine: TRUE POSITIVE (real violation) vs FALSE POSITIVE (false alarm)\n"
                "- Assess severity: Critical/High/Medium/Low/Info\n"
                "- Focus on MISRA C++ 2008 standard compliance\n"            
                "- Cross-reference with official MISRA C++ 2008 rules for validation\n"
                "- **IGNORE all CIDs with only [ \"select issue\" ] and no specific violation description**\n\n"
                
                "**REPORT FORMAT:**\n"
                "For each MISRA C++ CID WITH DETAILED DESCRIPTION:\n"
                "## 🔍 CID [number]: MISRA C++ Rule [X-Y-Z] Violation\n\n"
                "**Location:** Line [number] in [function name or global scope]\n\n"
                "**Rule Violated:** MISRA C++-2008 Rule [X-Y-Z] - [Rule description from standard]\n\n"
                "**Analysis Type:** [TRUE POSITIVE/FALSE POSITIVE]\n\n"
                "**Severity:** [Critical/High/Medium/Low/Info]\n\n"
                "**Violation Description:** [Detailed explanation of specific MISRA rule violation]\n\n"
                "**MISRA Rule Cross-Reference:** [Compare with official MISRA C++ 2008 standard]\n\n"
                "**Current Code:**\n"
                "```cpp\n[paste exact violating code with line numbers]\n```\n\n"
                
                "**Fixed Code:** (only for TRUE POSITIVE)\n"
                "```cpp\n[MISRA C++ compliant fixed code]\n```\n\n"
                
                "**Fix Explanation:** [Why this fix complies with MISRA C++ and is safer]\n\n"            
                "**Notes:** [Special context, acceptable deviations]\n\n"
                "---\n\n"
                
                "**FINAL SUMMARY:**\n"
                "- Total MISRA C++ CIDs WITH DETAILED DESCRIPTION detected: [X]\n"
                "- CIDs with only [ \"select issue\" ] ignored: [Y]\n"
                "- TRUE POSITIVE (needs immediate fix): [Z]\n"
                "- FALSE POSITIVE (can be ignored): [W]\n"
                "- Critical/High priority: [V] (highest priority)\n"                
                "- MISRA C++ 2008 compliance: [M] (standard cross-reference)\n\n"
                
                "**ACTION RECOMMENDATIONS:**\n"
                "1. Fix Critical/High severity MISRA violations with detailed descriptions immediately\n"
                "2. Document justified deviations with clear rationale\n"
                "3. Suppress FALSE POSITIVE with MISRA deviation comments\n"
                "4. Update coding guidelines to prevent future violations\n"
                "5. May review [ \"select issue\" ] CIDs separately if needed\n\n"
                
                "**IMPORTANT NOTES:**\n"
                "- **ANALYZE ONLY CIDs WITH SPECIFIC VIOLATION DESCRIPTIONS** - ignore [ \"select issue\" ]\n"
                "- Prioritize MISRA rules related to safety and reliability\n"
                "- For FALSE POSITIVE, explain clearly why rule doesn't apply\n"
                "- Suggest MISRA deviation comments: /* MISRA C++ Rule X-Y-Z deviation: [reason] */\n"
                "- Check consistency with overall MISRA C++ compliance strategy\n"
                "- Consider impact of fixes on overall code maintainability\n"
                "- Ensure fixes don't violate other rules\n"
                "- Always cross-reference with official MISRA C++ 2008 standard"
            )
        
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for CIM Static Analysis (Coverity) MISRA C++ result verification with MISRA C++ 2008 rule cross-reference.",
        )
        logger.info("CIM MISRA C++ check prompt completed")
        return result

    async def _handle_autosar_check(self) -> types.GetPromptResult:
        """Handle AUTOSAR C++ 14 code checking prompt"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++. Hãy phân tích file hiện tại để phát hiện vi phạm các quy tắc AUTOSAR C++ 14 cho phần mềm ô tô.\n"
                "Nếu chưa có file rule, hãy gọi fetch_autosar_rule từ MCP server.\n"
                "Luôn sử dụng bộ quy tắc AUTOSAR C++ 14 mới nhất vừa fetch để phân tích, không dùng rule cũ hoặc built-in.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Tìm TẤT CẢ vi phạm quy tắc trên\n"
                "- Tập trung vào vi phạm AUTOSAR C++ 14\n"
                "- Ghi rõ số hiệu rule (VD: Rule M0-1-1, Rule A0-1-1, MISRA Rule 8-4-3, DCL50-CPP)\n"
                "- Kiểm tra mọi dòng code, kể cả unreachable, dead code, return sớm, magic number\n"
                "- Kiểm tra mọi điểm acquire/release resource, mọi exit point, mọi function/method\n"
                "- Đưa ra code fix cụ thể cho từng lỗi\n"
                "- Ghi số dòng code gốc trong báo cáo\n\n"
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi lỗi:\n"
                "## 🚨 Vấn đề [#]: [Mô tả ngắn]\n\n"
                "**Rule vi phạm:** [SỐ HIỆU] - [Mô tả rule]\n\n"
                "**Vị trí:** [tên hàm hoặc global/unknown]\n\n"
                "**Mức độ:** [Critical/High/Medium/Low]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[code lỗi]\n```\n"
                "**Code đã sửa:**\n"
                "```cpp\n[code đúng]\n```\n"
                "**Giải thích:** [Vì sao vi phạm và cách sửa]\n\n"
                "**Lưu ý:** Nếu cần toàn bộ file code đã fix, hãy yêu cầu rõ ràng."
            )
        else:
            prompt = self.templates.get_autosar_analysis_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for AUTOSAR C++ 14 rule on current file.",
        )
        logger.info("AUTOSAR C++ 14 check prompt completed")
        return result

    async def _handle_misra_c_check(self) -> types.GetPromptResult:
        """Handle MISRA C 2023 code checking prompt"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C. Hãy phân tích file hiện tại để phát hiện vi phạm các quy tắc MISRA C 2023 cho phần mềm an toàn.\n"
                "Nếu chưa có file rule, hãy gọi fetch_misra_c_rule từ MCP server.\n"
                "Luôn sử dụng bộ quy tắc MISRA C 2023 mới nhất vừa fetch để phân tích, không dùng rule cũ hoặc built-in.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Tìm TẤT CẢ vi phạm quy tắc trên\n"
                "- Tập trung vào vi phạm MISRA C 2023 (NGÔN NGỮ C, KHÔNG PHẢI C++)\n"
                "- Ghi rõ số hiệu rule (VD: Rule 1.1, Dir 4.1, MISRA Rule 8-4-3, DCL50-CPP)\n"
                "- Kiểm tra mọi dòng code, kể cả unreachable, dead code, return sớm, magic number\n"
                "- Kiểm tra mọi điểm acquire/release resource, mọi exit point, mọi function\n"
                "- Đưa ra code fix cụ thể cho từng lỗi\n"
                "- Ghi số dòng code gốc trong báo cáo\n\n"
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi lỗi:\n"
                "## 🚨 Vấn đề [#]: [Mô tả ngắn]\n\n"
                "**Rule vi phạm:** [SỐ HIỆU] - [Mô tả rule]\n\n"
                "**Vị trí:** [tên hàm hoặc global/unknown]\n\n"
                "**Mức độ:** [Critical/High/Medium/Low]\n\n"
                "**Code hiện tại:**\n"
                "```c\n[code lỗi]\n```\n"
                "**Code đã sửa:**\n"
                "```c\n[code đúng]\n```\n"
                "**Giải thích:** [Vì sao vi phạm và cách sửa]\n\n"
                "**LưU Ý QUAN TRỌNG:** Đây là phân tích cho ngôn ngữ C (không phải C++). Tập trung vào MISRA C 2023 directives và rules."
            )
        else:
            prompt = self.templates.get_misra_c_analysis_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for MISRA C 2023 rule on current file.",
        )
        logger.info("MISRA C 2023 check prompt completed")
        return result

    async def _handle_race_condition_analysis(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """Handle race condition analysis prompt - always use fallback-style prompt with findings if available"""
        dir_path = get_src_dir()
        logger.info(f"[check_races] Using src_dir: {dir_path}")
        try:
            from lgedv.handlers.tool_handlers import ToolHandler
            tool_handler = ToolHandler()
            tool_result = await tool_handler._handle_detect_races({})
           
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                result = types.GetPromptResult(
                    messages=messages,
                    description="Race condition analysis (full result)",
                )
                logger.info("Race condition analysis prompt (fallback style) completed")
                return result
            else:
                logger.warning("No result from tool")
                return None
            
        except Exception as e:
            logger.error(f"Error in race condition analysis: {e}")
            return None
            
    async def _handle_memory_leak_analysis(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """Handle memory leak analysis prompt - always use fallback-style prompt with findings if available"""
        dir_path = get_src_dir()
        logger.info(f"[check_leaks] Using src_dir: {dir_path}")
        try:
            from lgedv.handlers.tool_handlers import ToolHandler
            tool_handler = ToolHandler()
            tool_result = await tool_handler._handle_memory_analysis({"dir_path": dir_path})
            
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                result = types.GetPromptResult(
                    messages=messages,
                    description="Memory leak analysis (full result)",
                )
                logger.info("Memory leak analysis prompt")
                return result
            else:
                logger.warning("No result from tool for memory leak analysis")
                return None
        except Exception as e:
            logger.error(f"Error in memory leak analysis: {e}")
            return None
           
       
    async def _handle_resource_leak_analysis(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """Handle resource leak analysis prompt - always use fallback-style prompt with findings if available, now with line numbers"""
        dir_path = get_src_dir()
        logger.info(f"[check_resources] Using src_dir: {dir_path}")
        try:
            from lgedv.handlers.tool_handlers import ToolHandler
            tool_handler = ToolHandler()
            # Also append the original findings text for reference
            tool_result = await tool_handler._handle_resource_analysis({})
            # logger.info(f"tool_result: {tool_result}")
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                result = types.GetPromptResult(
                    messages=messages,
                    description="Resource leak analysis (full prompt)",
                )
                logger.info("Resource leak analysis prompt completed")
                return result
            else:
                 logger.warning("No result from tool for resource leak analysis")
                 return None                 
        except Exception as e:
            logger.error(f"Error in resource leak analysis: {e}")
            return None

    # Thêm vào class PromptHandler

    async def _handle_reset_analysis_prompt(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """
        Handle reset analysis prompt - tự động gọi tool reset_analysic và trả về kết quả.
        """
        from lgedv.handlers.tool_handlers import ToolHandler
        tool_handler = ToolHandler()
        try:
            tool_result = await tool_handler._handle_reset_analysis({})
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                result = types.GetPromptResult(
                    messages=messages,
                    description="Reset analysis result.",
                )
                logger.info("Reset analysis prompt completed")
                return result
            else:
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text="No result from reset_analysic tool."),
                        )
                    ],
                    description="Reset analysis result (no output).",
                )
        except Exception as e:
            logger.error(f"Error in reset analysis prompt: {e}")
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=f"Error resetting analysis: {e}"),
                    )
                ],
                description="Reset analysis error.",
            )
    
    async def _handle_reset_mem_check_prompt(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """
        Handle reset_mem_check prompt - tự động gọi tool reset_mem_check và trả về kết quả.
        """
        from lgedv.handlers.tool_handlers import ToolHandler
        tool_handler = ToolHandler()
        try:
            tool_result = await tool_handler._handle_reset_mem_check({})
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                return types.GetPromptResult(
                    messages=messages,
                    description="Reset memory leak analysis result.",
                )
            else:
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text="No result from reset_mem_check tool."),
                        )
                    ],
                    description="Reset memory leak analysis result (no output).",
                )
        except Exception as e:
            logger.error(f"Error in reset_mem_check prompt: {e}")
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=f"Error resetting memory leak analysis: {e}"),
                    )
                ],
                description="Reset memory leak analysis error.",
            )

    async def _handle_reset_resource_check_prompt(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """
        Handle reset_resource_check prompt - tự động gọi tool reset_resource_check và trả về kết quả.
        """
        from lgedv.handlers.tool_handlers import ToolHandler
        tool_handler = ToolHandler()
        try:
            tool_result = await tool_handler._handle_reset_resource_check({})
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                return types.GetPromptResult(
                    messages=messages,
                    description="Reset resource leak analysis result.",
                )
            else:
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text="No result from reset_resource_check tool."),
                        )
                    ],
                    description="Reset resource leak analysis result (no output).",
                )
        except Exception as e:
            logger.error(f"Error in reset_resource_check prompt: {e}")
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=f"Error resetting resource leak analysis: {e}"),
                    )
                ],
                description="Reset resource leak analysis error.",
            )

    async def _handle_reset_race_check_prompt(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """
        Handle reset_race_check prompt - tự động gọi tool reset_race_check và trả về kết quả.
        """
        from lgedv.handlers.tool_handlers import ToolHandler
        tool_handler = ToolHandler()
        try:
            tool_result = await tool_handler._handle_reset_race_check({})
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                return types.GetPromptResult(
                    messages=messages,
                    description="Reset race analysis result.",
                )
            else:
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text="No result from reset_race_check tool."),
                        )
                    ],
                    description="Reset race analysis result (no output).",
                )
        except Exception as e:
            logger.error(f"Error in reset_race_check prompt: {e}")
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=f"Error resetting race analysis: {e}"),
                    )
                ],
                description="Reset race analysis error.",
            )
        
    async def _handle_design_check(self, arguments=None) -> types.GetPromptResult:
        import os
        from lgedv.modules.config import get_src_dir, get_req_dir, get_api_base_dirs, get_module_api, get_framework_dir, get_report_dir
        
        prompt_lang = os.environ.get("prompt_lang", "en")
        
        # Lấy tham số feature từ arguments dict
        feature = None
        if arguments and isinstance(arguments, dict) and "feature" in arguments:
            feature = arguments["feature"]
        
        logger.info(f"[check_design] Feature argument: {feature}")
        
        if prompt_lang == "vi":
            # Prompt tiếng Việt đầy đủ
            prompt = (
                "Bạn là chuyên gia phân tích thiết kế hệ thống nhúng ô tô.\n"
                "Nhiệm vụ của bạn: Đánh giá sơ đồ trình tự (sequence diagram) trong thiết kế đính kèm (file hình ảnh) về mức độ đáp ứng yêu cầu"
            )
            
            # Thêm feature nếu có
            if feature:
                prompt += f" cho feature {feature}"
            
            prompt += ", xác thực API, và độ robust.\n"
            
            # Tiếp tục với phần còn lại
            prompt += (
                "\n\n**QUY TRÌNH PHÂN TÍCH:**\n"
                f"1. Phân tích kỹ yêu cầu về feature"
            )
            
            if feature:
                prompt += f" {feature}"
            
            prompt += (
                " trong tài liệu requirement (file markdown đính kèm).\n"
                "2. Trích xuất đầy đủ các thành phần, API call, và luồng tương tác từ sequence diagram.\n"
                "3. Đối chiếu từng API call với ngữ cảnh ứng dụng, interface để xác thực tính hợp lệ.\n"
                "4. So sánh từng bước thiết kế với yêu cầu, kiểm tra điểm thiếu/phủ sóng hoặc chưa rõ ràng. Đặc biệt, cần phân tích kỹ các trường hợp lỗi (error case), timeout, và các tình huống bất thường có thể xảy ra trong thực tế.\n"
                "5. Đánh giá chi tiết khả năng xử lý lỗi, chiến lược recovery, logic fallback, và quản lý trạng thái của hệ thống. Nêu rõ các nhánh xử lý lỗi, cơ chế phục hồi, và đảm bảo hệ thống không rơi vào trạng thái bất định.\n"
                "6. Đề xuất cải tiến robust design, bổ sung các bước xử lý lỗi còn thiếu, và xây dựng sơ đồ PlantUML sequence cải tiến với nhánh error/recovery rõ ràng nếu cần.\n\n"
                "## 🔍 Phân tích thiết kế hiện tại\n"
                "### Đánh giá luồng trình tự\n"
                "- Thành phần: [liệt kê]\n"
                "- Luồng thông điệp: [phân tích]\n"
                "- Chuyển trạng thái: [phân tích]\n\n"
                "### Kết quả xác thực API\n"
                "**✅ API hợp lệ:**\n"
                "- `ClassName::method()` - Tìm thấy trong [ngữ cảnh]\n"
                "**❌ API thiếu:**\n"
                "- `UnknownClass::method()` - Không tìm thấy, cần bổ sung\n"
                "**⚠️ API mơ hồ:**\n"
                "- `CommonName::method()` - Tìm thấy ở nhiều ngữ cảnh, cần làm rõ\n\n"
                "### Đáp ứng yêu cầu\n"
                "| Mã yêu cầu | Mô tả | Trạng thái | Ghi chú |\n"
                "|-----------|-------|------------|--------|\n"
                "| REQ-001 | [nội dung] | ✅/❌/⚠️ | [ghi chú] |\n\n"
                "## ❌ Vấn đề nghiêm trọng\n"
                "- Thiếu phủ sóng yêu cầu\n"
                "- API không hợp lệ hoặc thiếu\n"
                "- Thiếu robust (xử lý lỗi, timeout, fallback, trạng thái)\n"
                "## 🚀 Giải pháp thiết kế nâng cao\n"
                "### Chiến lược tích hợp API\n"
                "- Dùng API có sẵn ở mọi ngữ cảnh nếu có thể\n"
                "- Sửa API hiện có nếu cần\n"
                "- Chỉ đề xuất API mới khi thực sự cần thiết, phải giải thích rõ\n\n"
                "### Kế hoạch đáp ứng yêu cầu\n"
                "- Với mỗi yêu cầu thiếu, nêu rõ thay đổi thiết kế cần thực hiện\n\n"
                "### Đề xuất improved design\n"
                "Vui lòng trình bày improved design cho thiết kế hiện tại bằng sequence diagram chuẩn PlantUML.\n"
                "```plantuml\n"
                "@startuml\n"
                "title Enhanced Design\n"
                "' Add enhanced design here\n"
                "' Include error handling and robustness\n"
                "@enduml\n"
                "```\n"
            )
            
            if feature:
                prompt += f" - {feature}"
            
            prompt += (
                "\n\n"
                "' Add enhanced design here\n"
                "' Include error handling and robustness\n"
                "@enduml\n"
                "```\n"
            )
        else:            
            prompt = self.templates.get_design_verification_prompt(feature)

        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for design verification and improvement.",
        )
        logger.info("Design verification prompt completed")
        return result
     
    def _format_resource_leak_summary(self, leaks: list) -> str:
        """Format a summary of resource leaks by type and severity"""
        summary = {}
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for leak in leaks:
            leak_type = leak.get('type', 'unknown')
            severity = leak.get('severity', 'medium')
            
            if leak_type not in summary:
                summary[leak_type] = 0
            
            summary[leak_type] += 1
            severity_counts[severity] += 1
        
        summary_text = f"**By Severity:** {severity_counts['critical']} Critical, {severity_counts['high']} High, {severity_counts['medium']} Medium, {severity_counts['low']} Low\n\n"
        summary_text += "**By Resource Type:**\n"
        
        for leak_type, count in summary.items():
            summary_text += f"- {leak_type.title()}: {count} leak(s)\n"
        
        return summary_text
    
    
    def _create_race_analysis_prompt_section(self, race_result: dict) -> str:
        """Create analysis prompt section with detailed race condition information (no grouping, no limit)"""
        prompt_section = "## 🎯 Priority Analysis Guidelines:\n\n"
        prompt_section += "1. Focus on shared state accessed by multiple threads.\n"
        prompt_section += "2. Ensure proper synchronization (mutexes, locks, atomics).\n"
        prompt_section += "3. Review thread creation and join/detach logic.\n"
        prompt_section += "4. Check for lock-free and concurrent data structure usage.\n"
        prompt_section += "5. Provide before/after code examples for fixes.\n\n"
        return prompt_section

    async def _handle_code_context(self) -> types.GetPromptResult:
        """Handle code context prompt (load and summarize all files in src_dir)"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là trợ lý ngữ cảnh mã nguồn. Nhiệm vụ của bạn là đọc và ghi nhớ toàn bộ nội dung, cấu trúc của tất cả các file mã nguồn (C++, Python, ...) trong thư mục dự án hiện tại.\n"
                "Nếu nội dung file chưa được tải, hãy gọi tool 'get_src_context' từ MCP server để lấy tất cả file mã nguồn trong thư mục SRC_DIR.\n"
                "Với mỗi file, hãy tóm tắt:\n"
                "- Tên file và đường dẫn tương đối\n"
                "- Tất cả class, struct, enum, function (C++, Python, ...)\n"
                "- Quan hệ kế thừa, sử dụng, thành phần\n"
                "- Biến toàn cục, hằng số, macro, cấu hình\n"
                "- Các chú thích hoặc tài liệu quan trọng\n"
                "Không thực hiện phân tích tĩnh hoặc kiểm tra rule ở bước này.\n"
                "Lưu ngữ cảnh này để dùng cho các truy vấn tiếp theo.\n\n"
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi file:\n"
                "### [Tên file]\n"
                "```[ngôn ngữ]\n[Tóm tắt cấu trúc, định nghĩa, điểm chính]\n```\n"
                "Lặp lại cho tất cả file.\n"
                "Xác nhận khi đã nạp đủ ngữ cảnh."
            )
        else:
            prompt = self.templates.get_context_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for loading and summarizing code context for all C++ files.",
        )
        logger.info("Code context prompt completed")
        return result