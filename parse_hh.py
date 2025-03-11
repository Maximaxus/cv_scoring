import requests
from bs4 import BeautifulSoup

###############################################################################
# Вспомогательная функция для безопасного получения текста одного элемента
###############################################################################
def find_text(soup, tag, attrs=None, default=""):
    """Ищет элемент <tag> с атрибутами attrs и возвращает text.strip().
       Если не найден, возвращает default (по умолчанию — пустая строка)."""
    element = soup.find(tag, attrs=attrs)
    return element.text.strip() if element else default

###############################################################################
# Функции для получения HTML и его обработки
###############################################################################
def get_html(url: str):
    return requests.get(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/58.0.3029.110 Safari/537.36"
            )
        },
        timeout=10  # На всякий случай ограничиваем время ожидания
    )

###############################################################################
# Парсинг информации о вакансии
###############################################################################
def extract_vacancy_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # Извлечение заголовка вакансии
    title = find_text(soup, "h1", {"data-qa": "vacancy-title"})

    # Извлечение зарплаты
    salary = find_text(soup, "span", {"data-qa": "vacancy-salary-compensation-type-net"})

    # Извлечение опыта работы
    experience = find_text(soup, "span", {"data-qa": "vacancy-experience"})

    # Извлечение типа занятости и режима работы
    employment_mode = find_text(soup, "p", {"data-qa": "vacancy-view-employment-mode"})

    # Извлечение компании
    company = find_text(soup, "a", {"data-qa": "vacancy-company-name"})

    # Извлечение местоположения
    location = find_text(soup, "p", {"data-qa": "vacancy-view-location"})

    # Извлечение описания вакансии
    description = find_text(soup, "div", {"data-qa": "vacancy-description"})

    # Извлечение ключевых навыков
    # На HH может быть много разных классов для навыков. Ниже — пример, используемый ранее.
    # Если навыки не найдены (find_all вернёт пустой список) — всё равно вернётся пустой список skills.
    skills_divs = soup.find_all("div", {"class": "magritte-tag__label___YHV-o_3-0-3"}) or []
    skills = [div.text.strip() for div in skills_divs]

    # Формирование строки в формате Markdown
    markdown = f"""
# {title}

**Компания:** {company}  
**Зарплата:** {salary}  
**Опыт работы:** {experience}  
**Тип занятости и режим работы:** {employment_mode}  
**Местоположение:** {location}

## Описание вакансии
{description}

## Ключевые навыки
- {'\n- '.join(skills)}
"""
    return markdown.strip()

def get_job_description(url: str):
    response = get_html(url)
    return extract_vacancy_data(response.text)

###############################################################################
# Парсинг информации о кандидате
###############################################################################
def extract_candidate_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # Пример: ищем заголовок (имя) по data-qa="bloko-header-1"
    # но не всегда такая структура есть, используем find_text для безопасности
    name = find_text(soup, "h2", {"data-qa": "bloko-header-1"})
    gender_age = ""
    location = ""
    job_title = ""
    job_status = ""

    # Иногда hh.ru меняет атрибуты, поэтому проверяем на всякий случай
    # В данном примере 'gender_age' берём из первого <p>, но возможно нужно уточнить.
    first_p = soup.find("p")
    if first_p:
        gender_age = first_p.text.strip()

    # Местоположение
    location = find_text(soup, "span", {"data-qa": "resume-personal-address"})
    
    # Текущая должность
    job_title = find_text(soup, "span", {"data-qa": "resume-block-title-position"})
    
    # Статус (например, "Ищу работу" или "Не ищу работу")
    job_status = find_text(soup, "span", {"data-qa": "job-search-status"})

    # Извлечение опыта работы
    experiences = []
    experience_section = soup.find("div", {"data-qa": "resume-block-experience"})
    if experience_section:
        experience_items = experience_section.find_all("div", class_="resume-block-item-gap")
        for item in experience_items:
            # Период (дата начала - дата окончания) + длительность
            period_div = item.find("div", class_="bloko-column_s-2")
            duration_div = item.find("div", class_="bloko-text")

            period = period_div.text.strip() if period_div else ""
            duration = duration_div.text.strip() if duration_div else ""

            if duration in period:
                # Если вдруг duration уже есть в period, не добавляем повторно
                pass
            elif duration:
                period += f" ({duration})"

            company_div = item.find("div", class_="bloko-text_strong")
            company = company_div.text.strip() if company_div else ""

            position_div = item.find("div", {"data-qa": "resume-block-experience-position"})
            position = position_div.text.strip() if position_div else ""

            description_div = item.find("div", {"data-qa": "resume-block-experience-description"})
            description = description_div.text.strip() if description_div else ""

            experiences.append(
                f"**{period}**\n\n*{company}*\n\n**{position}**\n\n{description}\n"
            )

    # Извлечение ключевых навыков
    skills = []
    skills_section = soup.find("div", {"data-qa": "skills-table"})
    if skills_section:
        skill_spans = skills_section.find_all("span", {"data-qa": "bloko-tag__text"}) or []
        skills = [s.text.strip() for s in skill_spans]

    # Формируем Markdown
    markdown = f"# {name}\n\n"
    markdown += f"**{gender_age}**\n\n"
    markdown += f"**Местоположение:** {location}\n\n"
    markdown += f"**Должность:** {job_title}\n\n"
    markdown += f"**Статус:** {job_status}\n\n"
    markdown += "## Опыт работы\n\n"
    for exp in experiences:
        markdown += exp + "\n"
    markdown += "## Ключевые навыки\n\n"
    markdown += ", ".join(skills) + "\n"

    return markdown.strip()

def get_candidate_info(url: str):
    response = get_html(url)
    return extract_candidate_data(response.text)
