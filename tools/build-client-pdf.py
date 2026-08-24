#!/usr/bin/env python3
"""Build the INTEGRI fillable information-request PDF (AcroForm)."""
import importlib.util, sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT = "/home/user/SECUMAX-SECURITY-WEBSITE"
OUT  = os.path.join(ROOT, "handover", "INTEGRI-Information-Request.pdf")
CREST = os.path.join(ROOT, "assets/img/favicon-512.png")

# reuse the exact content from the workbook builder
spec = importlib.util.spec_from_file_location(
    "bx", "/home/user/SECUMAX-SECURITY-WEBSITE/tools/build-client-workbook.py")
bx = importlib.util.module_from_spec(spec)
# stop it writing the xlsx on import
_save = None
import openpyxl
_orig_save = openpyxl.Workbook.save
openpyxl.Workbook.save = lambda self, *a, **k: None
spec.loader.exec_module(bx)
openpyxl.Workbook.save = _orig_save

SERVICES, COMPANY, PEOPLE, DOCUMENTS = bx.SERVICES, bx.COMPANY, bx.PEOPLE, bx.DOCUMENTS
HOLD, GROUP, LIVE = bx.HOLD, bx.GROUP, bx.LIVE

W, H = A4
M       = 38                 # page margin
CW      = W - 2 * M          # content width
RED     = HexColor("#C41520")
REDBR   = HexColor("#E01B24")
INK     = HexColor("#17141A")
MUTED   = HexColor("#6B6570")
RULE    = HexColor("#DCD9DE")
BAND    = HexColor("#0C0B0E")
SHADE   = HexColor("#F5F4F5")
FIELDBG = HexColor("#FFFBEF")

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("INTEGRI — Information Request")
c.setAuthor("INTEGRI Forensic Services (Pty) Ltd")
c.setSubject("Service confirmation and outstanding information")

page_no = 0
y = 0

# ---------------------------------------------------------------- helpers
def wrap(text, font, size, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if stringWidth(trial, font, size) <= width:
            cur = trial
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines

def footer():
    c.setFont("Helvetica", 7.5); c.setFillColor(MUTED)
    c.drawString(M, 24, "INTEGRI Forensic Services (Pty) Ltd  ·  Reg. 2026/561988/07")
    c.drawRightString(W - M, 24, f"Page {page_no}")

def new_page(running="Information Request"):
    global page_no, y
    if page_no: footer(); c.showPage()
    page_no += 1
    c.setFillColor(BAND); c.rect(0, H - 46, W, 46, stroke=0, fill=1)
    c.setFillColor(REDBR); c.rect(0, H - 49, W, 3, stroke=0, fill=1)
    try:
        c.drawImage(CREST, M, H - 40, width=30, height=30, mask="auto")
    except Exception:
        pass
    c.setFont("Helvetica-Bold", 11); c.setFillColor(white)
    c.drawString(M + 40, H - 29, "INTEGRI")
    c.setFont("Helvetica", 8); c.setFillColor(HexColor("#9C959F"))
    c.drawString(M + 40, H - 40, "Forensic & Protection Services")
    c.setFont("Helvetica", 8.5); c.setFillColor(white)
    c.drawRightString(W - M, H - 33, running)
    y = H - 76

def need(space, running="Information Request"):
    global y
    if y - space < 46:
        new_page(running)

def section(no, title, blurb=None):
    global y
    need(80)
    c.setFillColor(RED); c.setFont("Helvetica-Bold", 8)
    c.drawString(M, y, no.upper())
    y -= 15
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 16)
    c.drawString(M, y, title)
    y -= 6
    c.setStrokeColor(INK); c.setLineWidth(1.4); c.line(M, y, W - M, y)
    y -= 16
    if blurb:
        c.setFont("Helvetica", 9); c.setFillColor(MUTED)
        for ln in wrap(blurb, "Helvetica", 9, CW):
            c.drawString(M, y, ln); y -= 12
        y -= 6

def para(text, font="Helvetica", size=9.5, colour=None, lead=13, gap=8, width=None):
    global y
    colour = colour or INK
    for ln in wrap(text, font, size, width or CW):
        need(lead + 4)
        c.setFont(font, size); c.setFillColor(colour)
        c.drawString(M, y, ln); y -= lead
    y -= gap

# ---------------------------------------------------------------- cover
new_page("Information Request")
c.setFillColor(RED); c.setFont("Helvetica-Bold", 8.5)
c.drawString(M, y, "PLEASE COMPLETE AND RETURN")
y -= 26
c.setFillColor(INK); c.setFont("Helvetica-Bold", 26)
c.drawString(M, y, "Information Request")
y -= 26
c.setFont("Helvetica", 12); c.setFillColor(MUTED)
c.drawString(M, y, "Everything we need to finish your website")
y -= 26
c.setStrokeColor(REDBR); c.setLineWidth(3); c.line(M, y, M + 74, y)
y -= 22

para("Your website is built — 11 pages covering all seven divisions. Two things remain before "
     "it can go live: we need you to confirm that every service listed is one INTEGRI can actually "
     "deliver, and we need a handful of certificates and details that only you can supply.", gap=10)
para("Nothing is published until you have confirmed it is true. That is the whole point of this "
     "document.", gap=16)

# how to use
c.setFillColor(SHADE); c.rect(M, y - 96, CW, 96, stroke=0, fill=1)
c.setStrokeColor(REDBR); c.setLineWidth(2.5); c.line(M, y - 96, M, y)
yy = y - 16
c.setFillColor(INK); c.setFont("Helvetica-Bold", 10)
c.drawString(M + 14, yy, "How to complete this form"); yy -= 15
for t in ["This PDF is fillable. Open it in Adobe Acrobat Reader (free) or Preview on a Mac,",
          "click the boxes and type in the fields, then save and email it back to us.",
          "If you would rather work in a spreadsheet, use the Excel version we sent alongside it —",
          "same questions, easier to fill in on a phone."]:
    c.setFont("Helvetica", 9); c.setFillColor(MUTED)
    c.drawString(M + 14, yy, t); yy -= 13
y -= 112

# what we already have
c.setFillColor(INK); c.setFont("Helvetica-Bold", 11)
c.drawString(M, y, "Already confirmed — no action needed"); y -= 16
for label, val in [("Registered company name", "INTEGRI Forensic Services (Pty) Ltd"),
                   ("Company registration number", "2026/561988/07"),
                   ("Trading name on the website", "INTEGRI Forensic and Protection Services"),
                   ("Email address", "ops@integriforensicservices.com"),
                   ("Logo artwork", "Received and live on the site")]:
    c.setFont("Helvetica", 9); c.setFillColor(MUTED); c.drawString(M + 8, y, label)
    c.setFont("Helvetica-Bold", 9); c.setFillColor(INK); c.drawString(M + 190, y, val)
    y -= 14
y -= 10
c.setFont("Helvetica-Oblique", 8.5); c.setFillColor(MUTED)
for ln in wrap("We do not publish, and do not need, any ID numbers or residential addresses. "
               "The address on your CIPC certificate is residential and has deliberately been left "
               "off the website.", "Helvetica-Oblique", 8.5, CW):
    c.drawString(M, y, ln); y -= 11

# ---------------------------------------------------------------- A: services
new_page("Section A — Services")
section("Section A", "44 services we have taken off your website",
        "We compared the website against your business profile. These 44 services do not appear in the "
        "profile, so we have taken them off rather than advertise something we cannot back up. Nothing is "
        "deleted — tick TRUE against any INTEGRI actually does and it goes straight back on. Tick FALSE and "
        "it stays off for good.")

COL_REF, COL_SVC, COL_T, COL_F, COL_NOTE = 26, 236, 34, 34, 150
X_REF  = M
X_SVC  = X_REF + COL_REF
X_T    = X_SVC + COL_SVC + 6
X_F    = X_T + COL_T
X_NOTE = X_F + COL_F + 6

def svc_header():
    global y
    need(30, "Section A — Services")
    c.setFillColor(BAND); c.rect(M, y - 16, CW, 18, stroke=0, fill=1)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 7.5)
    c.drawString(X_REF + 2, y - 11, "REF")
    c.drawString(X_SVC + 2, y - 11, "SERVICE  /  WHAT HAS TO BE TRUE")
    c.drawCentredString(X_T + COL_T / 2, y - 11, "TRUE")
    c.drawCentredString(X_F + COL_F / 2, y - 11, "FALSE")
    c.drawString(X_NOTE + 2, y - 11, "YOUR NOTE")
    y -= 22

svc_header()
for no, div, all_items in SERVICES:
    items = [(n, t) for n, t in all_items if n in HOLD]
    if not items:
        continue
    need(46, "Section A — Services")
    c.setFillColor(SHADE); c.rect(M, y - 14, CW, 17, stroke=0, fill=1)
    c.setFillColor(RED); c.setFont("Helvetica-Bold", 9)
    c.drawString(X_REF + 2, y - 9, no)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 10)
    c.drawString(X_SVC + 2, y - 9, div)
    c.setFillColor(MUTED); c.setFont("Helvetica", 8)
    c.drawRightString(W - M - 4, y - 9, f"{len(items)} parked")
    y -= 22

    for i, (name, truth) in enumerate(items, start=1):
        ref = f"{no}.{i}"
        tl = wrap(truth, "Helvetica", 7.8, COL_SVC - 4)
        rh = 13 + len(tl) * 9.4 + 7
        if y - rh < 46:
            new_page("Section A — Services"); svc_header()
        top = y
        c.setFillColor(MUTED); c.setFont("Helvetica", 7.5)
        c.drawString(X_REF + 2, top - 9, ref)
        c.setFillColor(INK); c.setFont("Helvetica-Bold", 9)
        c.drawString(X_SVC + 2, top - 9, name)
        yy = top - 20
        c.setFillColor(MUTED); c.setFont("Helvetica", 7.8)
        for ln in tl:
            c.drawString(X_SVC + 2, yy, ln); yy -= 9.4

        gname = f"svc_{no}_{i}"
        bs = 11
        by = top - 15
        c.acroForm.radio(name=gname, value="TRUE", selected=False,
                         x=X_T + COL_T / 2 - bs / 2, y=by, size=bs,
                         buttonStyle="check", shape="square",
                         borderColor=HexColor("#9A939F"), fillColor=FIELDBG,
                         textColor=HexColor("#1F7A4D"), borderWidth=0.8, forceBorder=True)
        c.acroForm.radio(name=gname, value="FALSE", selected=False,
                         x=X_F + COL_F / 2 - bs / 2, y=by, size=bs,
                         buttonStyle="cross", shape="square",
                         borderColor=HexColor("#9A939F"), fillColor=FIELDBG,
                         textColor=RED, borderWidth=0.8, forceBorder=True)
        c.acroForm.textfield(name=f"note_{no}_{i}", value="",
                             x=X_NOTE, y=top - rh + 8, width=COL_NOTE, height=rh - 10,
                             fontSize=7.5, fontName="Helvetica",
                             borderColor=HexColor("#D6D2D9"), fillColor=FIELDBG,
                             textColor=INK, borderWidth=0.7, forceBorder=True,
                             fieldFlags="multiline")

        y = top - rh
        c.setStrokeColor(RULE); c.setLineWidth(0.4); c.line(M, y + 3, W - M, y + 3)

# ---------------------------------------------------------------- A2: now live
new_page("Section A2 — Live services")
section("Section A2", "What your website says today",
        "Taken straight from your business profile. No action needed unless something here is wrong — "
        "if it is, tell us and we will change it.")
for div, items in LIVE:
    need(30 + len(items) * 13, "Section A2 — Live services")
    c.setFillColor(SHADE); c.rect(M, y - 15, CW, 18, stroke=0, fill=1)
    c.setFillColor(RED); c.setFont("Helvetica-Bold", 9)
    c.drawString(M + 4, y - 10, div)
    c.setFillColor(MUTED); c.setFont("Helvetica", 8)
    c.drawRightString(W - M - 4, y - 10, f"{len(items)} live")
    y -= 24
    for nm in items:
        c.setFillColor(HexColor("#1F7A4D")); c.setFont("Helvetica-Bold", 8)
        c.drawString(M + 6, y, "LIVE")
        c.setFillColor(INK); c.setFont("Helvetica", 9)
        c.drawString(M + 40, y, nm)
        y -= 13
    y -= 8

# ---------------------------------------------------------------- B: company
new_page("Section B — Company details")
section("Section B", "Company details",
        "Type into the shaded boxes. Leave anything blank that does not apply to INTEGRI yet.")

B_LABEL_W = 150
B_FIELD_X = M + B_LABEL_W + 8
B_FIELD_W = 150
B_NOTE_X  = B_FIELD_X + B_FIELD_W + 8
B_NOTE_W  = (W - M) - B_NOTE_X          # whatever is actually left on the page

for idx, (label, value, note, editable) in enumerate(COMPANY):
    ll = wrap(label, "Helvetica-Bold", 8.8, B_LABEL_W)
    nl = wrap(note, "Helvetica-Oblique", 7.5, B_NOTE_W)
    rh = max(24, 12 + max(len(ll) * 10, len(nl) * 9))
    need(rh + 6, "Section B — Company details")
    top = y
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 8.8)
    for j, ln in enumerate(ll):
        c.drawString(M, top - 9 - j * 10, ln)
    if editable:
        c.acroForm.textfield(name=f"co_{idx}", value="",
                             x=B_FIELD_X, y=top - 18, width=B_FIELD_W, height=15,
                             fontSize=8.5, fontName="Helvetica",
                             borderColor=HexColor("#D6D2D9"), fillColor=FIELDBG,
                             textColor=INK, borderWidth=0.7, forceBorder=True)
    else:
        c.setFont("Helvetica-Bold", 8.2); c.setFillColor(HexColor("#1F7A4D"))
        for j, ln in enumerate(wrap(value, "Helvetica-Bold", 8.2, B_FIELD_W)):
            c.drawString(B_FIELD_X, top - 9 - j * 10, ln)
    c.setFillColor(MUTED); c.setFont("Helvetica-Oblique", 7.5)
    for j, ln in enumerate(nl):
        c.drawString(B_NOTE_X, top - 9 - j * 9, ln)
    y = top - rh
    c.setStrokeColor(RULE); c.setLineWidth(0.4); c.line(M, y + 4, W - M, y + 4)

# ---------------------------------------------------------------- C: people
new_page("Section C — People")
section("Section C", "People and roles",
        "Names and the job title we should publish. The Information Officer is required by law "
        "because the website collects enquiries. Please do not send ID numbers — we neither publish "
        "nor need them.")

for idx, (who, f1, f2, f3, note) in enumerate(PEOPLE):
    nl = wrap(note, "Helvetica-Oblique", 7.5, CW - 8)
    rh = 62 + len(nl) * 9
    need(rh + 6, "Section C — People")
    top = y
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 10)
    c.drawString(M, top - 10, who)
    fw = (CW - 16) / 3
    for k, cap in enumerate([f1, f2, f3]):
        x = M + k * (fw + 8)
        c.setFillColor(MUTED); c.setFont("Helvetica", 7)
        c.drawString(x, top - 24, cap.upper())
        c.acroForm.textfield(name=f"person_{idx}_{k}", value="",
                             x=x, y=top - 42, width=fw, height=15,
                             fontSize=8.5, fontName="Helvetica",
                             borderColor=HexColor("#D6D2D9"), fillColor=FIELDBG,
                             textColor=INK, borderWidth=0.7, forceBorder=True)
    c.setFillColor(MUTED); c.setFont("Helvetica-Oblique", 7.5)
    for j, ln in enumerate(nl):
        c.drawString(M, top - 52 - j * 9, ln)
    y = top - rh
    c.setStrokeColor(RULE); c.setLineWidth(0.4); c.line(M, y + 4, W - M, y + 4)

# ---------------------------------------------------------------- D: documents
new_page("Section D — Documents")
section("Section D", "Documents to attach",
        "Tick each one as you attach it to your reply. If something does not exist yet, leave it "
        "unticked and tell us — we will take the matching claim off the website rather than leave "
        "it unsupported.")

D_WHY_X = M + 262
D_WHY_W = (W - M) - D_WHY_X

for idx, (doc, why) in enumerate(DOCUMENTS):
    received = why.startswith("RECEIVED")
    wl = wrap(why, "Helvetica", 7.8, D_WHY_W)
    rh = max(22, 12 + len(wl) * 9)
    need(rh + 6, "Section D — Documents")
    top = y
    if received:
        c.setFillColor(HexColor("#1F7A4D")); c.setFont("Helvetica-Bold", 9)
        c.drawString(M, top - 10, "DONE")
    else:
        c.acroForm.checkbox(name=f"doc_{idx}", checked=False,
                            x=M, y=top - 14, size=11, buttonStyle="check",
                            borderColor=HexColor("#9A939F"), fillColor=FIELDBG,
                            textColor=HexColor("#1F7A4D"), borderWidth=0.8, forceBorder=True)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 9)
    c.drawString(M + 34, top - 10, doc)
    c.setFillColor(MUTED); c.setFont("Helvetica", 7.8)
    for j, ln in enumerate(wl):
        c.drawString(D_WHY_X, top - 10 - j * 9, ln)
    y = top - rh
    c.setStrokeColor(RULE); c.setLineWidth(0.4); c.line(M, y + 4, W - M, y + 4)

y -= 14
need(90, "Section D — Documents")
c.setFillColor(SHADE); c.rect(M, y - 74, CW, 74, stroke=0, fill=1)
c.setStrokeColor(REDBR); c.setLineWidth(2.5); c.line(M, y - 74, M, y)
yy = y - 16
c.setFillColor(INK); c.setFont("Helvetica-Bold", 10)
c.drawString(M + 14, yy, "When you are done"); yy -= 15
for t in ["Save this PDF (or the Excel version), attach the certificates you have ticked,",
          "and email it all back to us. Anything still outstanding can follow later —",
          "send what you have rather than waiting until everything is ready."]:
    c.setFont("Helvetica", 9); c.setFillColor(MUTED)
    c.drawString(M + 14, yy, t); yy -= 13

footer()
c.save()
print("written:", OUT, f"{os.path.getsize(OUT)/1024:.1f} KB")
