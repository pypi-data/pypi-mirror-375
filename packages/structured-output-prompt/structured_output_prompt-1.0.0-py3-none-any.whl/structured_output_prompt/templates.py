from typing import Dict

# 多语言模板字典，占位符 {model_desc} 用于替换 generate_model_description
DEFAULT_TEMPLATES: Dict[str, str] = {
    "zh": (
        "严格按照下面要求输出：\n"
        "你必须返回实际的完整内容作为最终答案，而不是摘要。\n"
        "仅输出一个 JSON 对象；不要输出任何解释、前后缀、空行或 Markdown 代码块。\n"
        "确保你的最终答案只包含以下格式的内容：{model_desc}"
    ),
    "en": (
        "Output strictly according to the following requirements:\n"
        "You must return the actual complete content as the final answer, not a summary.\n"
        "Output only one JSON object; do not output any explanations, prefixes, suffixes, blank lines, or Markdown code blocks.\n"
        "Ensure your final answer contains only the following format: {model_desc}"
    ),
    "ja": (
        "以下の要件に厳密に従って出力してください：\n"
        "最終回答として実際の完全な内容を返さなければなりません。要約ではありません。\n"
        "JSON オブジェクトを 1 つだけ出力してください。説明、前後接頭辞、空行、Markdown コードブロックを出力しないでください。\n"
        "最終回答が以下の形式の内容のみを含むことを確認してください：{model_desc}"
    ),
    "de": (
        "Ausgabe streng nach den folgenden Anforderungen:\n"
        "Sie müssen den tatsächlichen vollständigen Inhalt als endgültige Antwort zurückgeben, nicht als Zusammenfassung.\n"
        "Geben Sie nur ein JSON-Objekt aus; geben Sie keine Erklärungen, Präfixe, Suffixe, Leerzeilen oder Markdown-Codeblöcke aus.\n"
        "Stellen Sie sicher, dass Ihre endgültige Antwort nur den folgenden Format enthält: {model_desc}"
    ),
    "fr": (
        "Sortie strictement selon les exigences suivantes :\n"
        "Vous devez retourner le contenu complet réel comme réponse finale, pas un résumé.\n"
        "Sortez seulement un objet JSON ; ne sortez aucune explication, préfixes, suffixes, lignes vides ou blocs de code Markdown.\n"
        "Assurez-vous que votre réponse finale contient seulement le format suivant : {model_desc}"
    ),
    "es": (
        "Salida estrictamente según los siguientes requisitos:\n"
        "Debes devolver el contenido completo real como respuesta final, no un resumen.\n"
        "Salida solo un objeto JSON; no salidas explicaciones, prefijos, sufijos, líneas en blanco o bloques de código Markdown.\n"
        "Asegúrate de que tu respuesta final contenga solo el siguiente formato: {model_desc}"
    ),
    "pt": (
        "Saída estritamente de acordo com os seguintes requisitos:\n"
        "Você deve retornar o conteúdo completo real como resposta final, não um resumo.\n"
        "Saída apenas um objeto JSON; não saídas explicações, prefixos, sufixos, linhas em branco ou blocos de código Markdown.\n"
        "Certifique-se de que sua resposta final contenha apenas o seguinte formato: {model_desc}"
    ),
    "ru": (
        "Вывод строго по следующим требованиям:\n"
        "Вы должны вернуть фактическое полное содержание как окончательный ответ, а не резюме.\n"
        "Выводите только один объект JSON; не выводите объяснения, префиксы, суффиксы, пустые строки или блоки кода Markdown.\n"
        "Убедитесь, что ваш окончательный ответ содержит только следующий формат: {model_desc}"
    ),
    "ko": (
        "다음 요구 사항에 따라 엄격하게 출력하십시오:\n"
        "최종 답변으로 실제 완전한 내용을 반환해야 합니다. 요약이 아닙니다.\n"
        "JSON 객체 하나만 출력하십시오. 설명, 접두사, 접미사, 빈 줄 또는 Markdown 코드 블록을 출력하지 마십시오.\n"
        "최종 답변이 다음 형식의 내용만 포함하는지 확인하십시오: {model_desc}"
    ),
}
