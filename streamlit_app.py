import openai
import streamlit as st
from parse_hh import get_candidate_info, get_job_description

# Указываем API-ключ через st.secrets (безопасный способ)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Вывод версии openai для отладки
st.write("Текущая версия openai:", openai.__version__)

SYSTEM_PROMPT = """
Задача:
Оцени, насколько кандидат подходит для данной вакансии, учитывая его профессиональный опыт, навыки, соответствие требованиям и умение полно и чётко описывать свою работу.

Инструкции по оценке:
1. Аналитический комментарий.
   - Сформулируй краткое обоснование оценки, опираясь на ключевые компетенции и требования вакансии.
   - Отметь сильные стороны кандидата и возможные пробелы в опыте.

2. Качество резюме.
   - Оцени, насколько понятно описан опыт работы и решаемые задачи.
   - Укажи, в какой мере кандидат способен структурированно и логично рассказывать о своих обязанностях и достижениях.
   - Учти эту оценку в общем выводе, поскольку важно, чтобы соискатель умел чётко формулировать свой опыт.

3. Итоговая оценка.
   - Сведи результаты анализа и качество представленных данных в одну итоговую цифру.
   - Укажи общий уровень соответствия кандидата вакансии в процентах от 0% до 100%.

Формат ответа:
- Отвечай максимально сжато, не более 100 слов.
- Короткое текстовое резюме (аналитический комментарий), где кратко изложены основные аргументы в пользу или против найма.
- Отдельная оценка качества заполнения резюме.
- Итоговый показатель в процентах (0–100), отражающий совокупную оценку кандидата.
""".strip()

def request_gpt(system_prompt, user_prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Или "gpt-4", если у вас есть к ней доступ
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0
        )
        # Доступ к ответу через словарный ключ "message"
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Ошибка при запросе к OpenAI: {e}")
        return None

st.title("CV Scoring App")

job_description_url = st.text_area("Enter the job description URL")
cv_url = st.text_area("Enter the CV URL")

if st.button("Score CV"):
    with st.spinner("Scoring CV..."):
        job_description = get_job_description(job_description_url)
        cv = get_candidate_info(cv_url)

        st.write("Job description:")
        st.write(job_description)
        st.write("CV:")
        st.write(cv)

        user_prompt = f"# ВАКАНСИЯ\n{job_description}\n\n# РЕЗЮМЕ\n{cv}"
        response = request_gpt(SYSTEM_PROMPT, user_prompt)
    if response:
        st.write("**Результат:**")
        st.write(response)
