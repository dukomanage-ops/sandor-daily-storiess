"""Build the branded daily market brief PDF (letter size)."""
import sys, os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit

F = os.environ.get("FONT_DIR", "/home/claude/fonts")
for n in ["Cormorant-Regular", "Cormorant-Medium", "Montserrat-Regular", "Montserrat-Medium", "Montserrat-SemiBold"]:
    pdfmetrics.registerFont(TTFont(n, f"{F}/{n}.ttf"))
EM, IV, ON, AU, SA, GR, HA = map(HexColor, ["#0B3D2E", "#F7F5F0", "#222222", "#116248", "#A9C9B8", "#6B6B66", "#E2DED4"])
W, H = letter
M = 60

SECTIONS = [
    ("APPRAISALS", "45–50 pages", "What the appraisal overhaul means for your deals",
     "New appraisal reports will include considerably more property detail, with some running 45 to 50 pages or longer. Lenders may qualify for temporary exceptions during the transition.",
     ["Ask your lender whether their appraisal provider is ready for the new format.",
      "Give the appraiser accurate, complete property information up front.",
      "Build realistic financing deadlines into contracts to absorb possible delays."]),
    ("FINANCING", "January", "HUD talks more homes, more buyers in Florida",
     "HUD Secretary Scott Turner brought his homeownership message to Florida, outlining plans to encourage more homebuilding and help younger Americans qualify for mortgages.",
     ["More construction could eventually mean more choices for Florida buyers on a budget.",
      "New FHA credit-scoring options arriving in January could help some renters with limited credit histories qualify.",
      "Renters who were told 'not yet' may be worth a second conversation in the new year."]),
    ("BUYER TRENDS", "2 offices", "One home office? Buyers are asking for a second",
     "Home offices are high on the wish list for new-construction buyers, with hobby rooms and playrooms close behind. Flexible space deserves a closer look.",
     ["Ask buyers what they need extra rooms to do: work, hobbies or family.",
      "Show how bonus rooms and flex spaces can serve more than one use.",
      "Describe functional spaces accurately in listings rather than assuming one setup fits all."]),
]


def horizon(c, x1, x2, y, col):
    c.setStrokeColor(col); c.setLineWidth(0.75); c.line(x1, y, x2 - 6, y)
    c.setFillColor(col); s = 4
    p = c.beginPath(); p.moveTo(x2 - s, y); p.lineTo(x2, y + s); p.lineTo(x2 + s, y); p.lineTo(x2, y - s); p.close()
    c.drawPath(p, fill=1, stroke=0)


def tracked(c, x, y, text, font, size, col, sp):
    c.setFillColor(col); t = c.beginText(x, y); t.setFont(font, size); t.setCharSpace(sp); t.textOut(text); t.setCharSpace(0); c.drawText(t)


def para(c, x, y, text, font, size, col, width, lead):
    c.setFillColor(col); c.setFont(font, size)
    for line in simpleSplit(text, font, size, width):
        c.drawString(x, y, line); y -= lead
    return y


def footer(c, dark=False):
    col = SA if dark else GR
    c.setStrokeColor(HA if not dark else SA); c.setLineWidth(0.5); c.line(M, 62, W - M, 62)
    c.setFont("Montserrat-Regular", 7.5); c.setFillColor(col)
    c.drawString(M, 46, "Sandor Hernandez · Commercial & Investment Realtor | Aura Homes · FL Lic. SL3611191")
    c.drawString(M, 34, "786.799.2069 · info@sandorsrealty.com · sandorsrealty.com")
    c.drawRightString(W - M, 34, "Source: Florida Realtors daily news, Oct. 20, 2026")


def main(out):
    c = canvas.Canvas(out, pagesize=letter)
    c.setTitle("Miami Market Brief — Oct 20, 2026"); c.setAuthor("Sandor Hernandez | Aura Homes")
    # cover
    c.setFillColor(EM); c.rect(0, 0, W, H, fill=1, stroke=0)
    tracked(c, M, H - 80, "SANDOR HERNANDEZ", "Cormorant-Medium", 13, IV, 3.5)
    horizon(c, M, M + 170, H - 92, SA)
    tracked(c, M, H - 300, "MIAMI MARKET BRIEF · TUESDAY, OCTOBER 20, 2026", "Montserrat-SemiBold", 9, SA, 2)
    c.setFillColor(IV); c.setFont("Cormorant-Regular", 54)
    for i, l in enumerate(["Three things moving", "Florida deals today."]):
        c.drawString(M, H - 360 - i * 60, l)
    horizon(c, M, M + 140, H - 470, SA)
    para(c, M, H - 505, "Appraisals are getting longer, FHA financing is opening up for thin-credit buyers, and new-construction buyers want more flexible space. Here's what each means for your next deal.",
         "Montserrat-Regular", 11.5, IV, W - 2 * M - 80, 18)
    c.setFillColor(SA); c.setFont("Cormorant-Regular", 22); c.drawString(M, 140, "Have a deal in mind? Let's run the numbers.")
    footer(c, dark=True); c.showPage()

    # content page
    c.setFillColor(IV); c.rect(0, 0, W, H, fill=1, stroke=0)
    tracked(c, M, H - 60, "SANDOR HERNANDEZ", "Cormorant-Medium", 11, ON, 3)
    horizon(c, M, M + 145, H - 70, AU)
    y = H - 115
    for i, (lab, hero, title, summ, bullets) in enumerate(SECTIONS, 1):
        tracked(c, M, y, f"{i:02d}  ·  {lab}", "Montserrat-SemiBold", 8, AU, 1.8)
        c.setFillColor(AU); c.setFont("Cormorant-Regular", 30); c.drawRightString(W - M, y - 18, hero)
        y -= 30
        y = para(c, M, y, title, "Cormorant-Regular", 20, ON, W - 2 * M - 200, 23) - 6
        y = para(c, M, y, summ, "Montserrat-Regular", 9.5, ON, W - 2 * M, 14) - 6
        tracked(c, M, y, "PUT IT TO WORK", "Montserrat-SemiBold", 7, GR, 1.4); y -= 14
        for b in bullets:
            c.setFillColor(AU); c.rect(M + 1, y + 2.5, 3, 3, fill=1, stroke=0)
            y = para(c, M + 14, y, b, "Montserrat-Regular", 9.5, ON, W - 2 * M - 14, 14) - 2
        y -= 14
        if i < len(SECTIONS):
            c.setStrokeColor(HA); c.setLineWidth(0.5); c.line(M, y + 6, W - M, y + 6); y -= 18
    footer(c); c.save()
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
