import re
import yamja


def normalize_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()


def test_render_template():
    config = yamja.load_config('tests/data/test_render.yaml')

    expected_output = """
    <CHARACTER>
      <NAME>Jane Doe</NAME>
      <AGE>30</AGE>
      <SKILLS>
          <SKILL>hacking</SKILL>
          <SKILL>parkour</SKILL>
          <SKILL>martial arts</SKILL>
      </SKILLS>
    </CHARACTER>"""
    expected_output = normalize_whitespace(expected_output)

    rendered = config.render('character_prompt', character=config.lookup('characters.jane'))
    rendered = normalize_whitespace(rendered)

    assert rendered == expected_output
