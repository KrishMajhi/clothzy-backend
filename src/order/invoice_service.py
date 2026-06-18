from io import BytesIO
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

BLACK = colors.HexColor("#111111")
CREAM = colors.HexColor("#F5F0E8")
GOLD  = colors.HexColor("#C9A84C")
LIGHT = colors.HexColor("#F9F7F3")
MUTED = colors.HexColor("#888888")
WHITE = colors.white


def _s():
    base = getSampleStyleSheet()
    def p(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)
    return {
        "brand":         p("brand",         fontSize=26, fontName="Helvetica-Bold",  textColor=BLACK, leading=30),
        "tagline":       p("tagline",        fontSize=8,  fontName="Helvetica",       textColor=MUTED, letterSpacing=3),
        "inv_label":     p("inv_label",      fontSize=9,  fontName="Helvetica-Bold",  textColor=GOLD,  letterSpacing=2, alignment=TA_RIGHT),
        "inv_id":        p("inv_id",         fontSize=18, fontName="Helvetica-Bold",  textColor=BLACK, alignment=TA_RIGHT, leading=22),
        "date":          p("date",           fontSize=8,  fontName="Helvetica",       textColor=MUTED, alignment=TA_RIGHT),
        "section":       p("section",        fontSize=7,  fontName="Helvetica-Bold",  textColor=GOLD,  letterSpacing=2, spaceAfter=4),
        "body":          p("body",           fontSize=9,  fontName="Helvetica",       textColor=BLACK, leading=14),
        "muted":         p("muted",          fontSize=8,  fontName="Helvetica",       textColor=MUTED, leading=12),
        "th":            p("th",             fontSize=8,  fontName="Helvetica-Bold",  textColor=WHITE),
        "td":            p("td",             fontSize=9,  fontName="Helvetica",       textColor=BLACK, leading=13),
        "td_sub":        p("td_sub",         fontSize=8,  fontName="Helvetica",       textColor=MUTED, leading=11),
        "td_r":          p("td_r",           fontSize=9,  fontName="Helvetica-Bold",  textColor=BLACK, alignment=TA_RIGHT),
        "total_lbl":     p("total_lbl",      fontSize=10, fontName="Helvetica-Bold",  textColor=BLACK),
        "total_val":     p("total_val",      fontSize=13, fontName="Helvetica-Bold",  textColor=GOLD,  alignment=TA_RIGHT),
        "footer":        p("footer",         fontSize=7,  fontName="Helvetica",       textColor=MUTED, alignment=TA_CENTER),
    }


def _fmt(val: str) -> str:
    return val.replace("_", " ").title()

def _dt(dt) -> str:
    return dt.strftime("%d %B %Y, %I:%M %p") if isinstance(dt, datetime) else str(dt)

def _money(val) -> str:
    return f"₹{float(val):,.2f}"


class InvoiceService:

    def generate_invoice(self, order, order_items) -> bytes:
        buffer = BytesIO()
        W, H = A4
        M = 18 * mm
        col = W - 2 * M

        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                leftMargin=M, rightMargin=M,
                                topMargin=M, bottomMargin=M)
        S = _s()
        els = []

        # ── HEADER ────────────────────────────────────────────────
        hdr = Table([[
            [Paragraph("CLOTHZY", S["brand"]),
             Paragraph("FASHION · QUALITY · STYLE", S["tagline"])],
            [Paragraph("INVOICE", S["inv_label"]),
             Paragraph(f"#{str(order.id)[:8].upper()}", S["inv_id"]),
             Paragraph(_dt(order.created_at), S["date"])],
        ]], colWidths=[col * 0.5, col * 0.5])
        hdr.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ]))
        els += [hdr, Spacer(1, 6),
                HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=12)]

        # ── BILL TO  |  ORDER INFO ────────────────────────────────
        addr_parts = filter(None, [
            order.address_line_1,
            order.address_line_2,
            f"{order.city}, {order.state} – {order.postal_code}",
            order.country,
        ])

        bill = [
            Paragraph("BILL TO", S["section"]),
            Paragraph(f"<b>{order.delivery_name}</b>", S["body"]),
            Paragraph(order.delivery_phone, S["muted"]),
            Spacer(1, 4),
            Paragraph("<br/>".join(addr_parts), S["muted"]),
        ]

        info_rows = [
            ("Order ID",        str(order.id)),
            ("Date",            _dt(order.created_at)),
            ("Order Status",    _fmt(order.status)),
            ("Payment Method",  _fmt(order.payment_method)),
            ("Payment Status",  _fmt(order.payment_status)),
            ("Shipping Method", _fmt(order.shipping_method)),
        ]
        if order.promo_code:
            info_rows.append(("Promo Code", order.promo_code))

        info_tbl = Table(
            [[Paragraph(k, S["muted"]), Paragraph(v, S["body"])] for k, v in info_rows],
            colWidths=[col * 0.26, col * 0.24],
        )
        info_tbl.setStyle(TableStyle([
            ("TOPPADDING",    (0,0), (-1,-1), 2),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2),
            ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ]))

        meta = Table([[bill, info_tbl]], colWidths=[col * 0.44, col * 0.56])
        meta.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ]))
        els += [meta, Spacer(1, 14),
                HRFlowable(width="100%", thickness=0.5,
                           color=colors.HexColor("#DDDDDD"), spaceAfter=6)]

        # ── ITEMS TABLE ───────────────────────────────────────────
        # Columns: Product | Size | Color | Qty | Unit Price | Subtotal
        cw = [col * w for w in (0.32, 0.12, 0.13, 0.08, 0.17, 0.18)]

        rows = [[Paragraph(h, S["th"]) for h in
                 ("PRODUCT", "SIZE", "COLOR", "QTY", "UNIT PRICE", "SUBTOTAL")]]

        for item in order_items:
            rows.append([
                Paragraph(item.product_name, S["td"]),
                Paragraph(item.selected_size, S["td"]),
                Paragraph(item.selected_color.title(), S["td"]),
                Paragraph(str(item.quantity), S["td"]),
                Paragraph(_money(item.price_at_purchase), S["td"]),
                Paragraph(_money(item.subtotal), S["td_r"]),
            ])

        items_tbl = Table(rows, colWidths=cw, repeatRows=1)
        items_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), BLACK),
            ("TOPPADDING",    (0,0), (-1,0), 8),
            ("BOTTOMPADDING", (0,0), (-1,0), 8),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("RIGHTPADDING",  (0,0), (-1,-1), 8),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
            ("TOPPADDING",    (0,1), (-1,-1), 7),
            ("BOTTOMPADDING", (0,1), (-1,-1), 7),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN",         (3,0), (5,-1), "RIGHT"),
            ("LINEBELOW",     (0,0), (-1,-1), 0.3, colors.HexColor("#EEEEEE")),
            ("BOX",           (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
        ]))
        els += [items_tbl, Spacer(1, 14)]

        # ── SUMMARY ───────────────────────────────────────────────
        summary = [
            ("Subtotal",        _money(order.subtotal)),
            ("Tax",             _money(order.tax)),
            ("Delivery Charge", _money(order.delivery_charge)),
            ("Shipping Charge", _money(order.shipping_charge)),
            ("Discount",        f"– {_money(order.discount)}"),
        ]
        sum_data = [
            [Paragraph(k, S["muted"]), Paragraph(v, S["td_r"])]
            for k, v in summary
        ] + [[
            Paragraph("TOTAL AMOUNT", S["total_lbl"]),
            Paragraph(_money(order.total_amount), S["total_val"]),
        ]]

        sum_tbl = Table(sum_data, colWidths=[col * 0.25, col * 0.25])
        sum_tbl.setStyle(TableStyle([
            ("TOPPADDING",    (0,0), (-1,-2), 3),
            ("BOTTOMPADDING", (0,0), (-1,-2), 3),
            ("TOPPADDING",    (0,-1), (-1,-1), 8),
            ("BOTTOMPADDING", (0,-1), (-1,-1), 8),
            ("LINEABOVE",     (0,-1), (-1,-1), 1.5, GOLD),
            ("BACKGROUND",    (0,-1), (-1,-1), CREAM),
        ]))

        els.append(Table([["", sum_tbl]], colWidths=[col * 0.5, col * 0.5]))

        # ── FOOTER ────────────────────────────────────────────────
        els += [
            Spacer(1, 20),
            HRFlowable(width="100%", thickness=0.5,
                       color=colors.HexColor("#DDDDDD"), spaceAfter=8),
            Paragraph(
                "Thank you for shopping with Clothzy · clothsite.in · support@clothzy.in",
                S["footer"],
            ),
            Paragraph(
                "This is a system-generated invoice and does not require a signature.",
                S["footer"],
            ),
        ]

        doc.build(els)
        buffer.seek(0)
        return buffer.getvalue()