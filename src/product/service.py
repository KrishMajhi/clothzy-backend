from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, desc, or_

from .schemas.productmodel import ProductCreateModel, ProductSort, ProductUpdateModel
from .model import Product


class ProductService:

    # ════════════════════════════════════════════════════════
    # GET ALL PRODUCTS (paginated + filtered)
    # ════════════════════════════════════════════════════════
    async def get_all_products(
        self,
        session: AsyncSession,
        material: str | None = None,
        category: str | None = None,
        gender: str | None = None,
        sort_by: str | None = None,
        max_range: str | None = None,
        search: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        sizes: str | None = None,
        colors: str | None = None,
    ):
        stmt = select(Product)

        # ── Filters ─────────────────────────────────────────
        if material:
            stmt = stmt.where(Product.material.ilike(f"%{material}%"))

        if category:
            cats = category.split(",")
            stmt = stmt.where(Product.category.in_(cats))

        if sizes:
            selected = sizes.split(",")
            stmt = stmt.where(or_(*[Product.sizes.contains([s]) for s in selected]))

        if colors:
            selected = colors.split(",")
            stmt = stmt.where(or_(*[Product.colors.contains([c]) for c in selected]))

        if gender:
            stmt = stmt.where(Product.gender == gender)

        if max_range:
            try:
                stmt = stmt.where(
                    Product.price >= 0,
                    Product.price <= float(max_range),
                )
            except ValueError:
                pass  # ignore invalid max_range values

        if search:
            # print(str(Product.tags))
            stmt = stmt.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                    Product.brand.ilike(f"%{search}%"),
                    Product.category.ilike(f"%{search}%"),
                    Product.material.ilike(f"%{search}%"),
                    Product.colors.contains([search]),
                    Product.tags.contains([search]),
                )
            )
            print(stmt)

        # ── Sorting ──────────────────────────────────────────
        if sort_by == "newest":
            stmt = stmt.order_by(desc(Product.created_at))
        elif sort_by == "oldest":
            stmt = stmt.order_by(Product.created_at)
        elif sort_by == "price_low_to_high":
            stmt = stmt.order_by(Product.price)
        elif sort_by == "price_high_to_low":
            stmt = stmt.order_by(desc(Product.price))
        elif sort_by == "rating":
            stmt = stmt.order_by(desc(Product.rating))
        else:
            stmt = stmt.order_by(desc(Product.created_at))  # default

        # ── Pagination ───────────────────────────────────────
        if limit is not None and page is not None:
            offset = (page - 1) * limit
            stmt = stmt.offset(offset).limit(limit)

        result = await session.exec(stmt)
        return result.all()

    # ════════════════════════════════════════════════════════
    # COUNT PRODUCTS (same filters, no pagination)
    # Used by the route to return accurate total + total_pages
    # ════════════════════════════════════════════════════════
    async def count_products(
        self,
        session: AsyncSession,
        material: str | None = None,
        category: str | None = None,
        gender: str | None = None,
        max_range: str | None = None,
        search: str | None = None,
        sizes: str | None = None,
        colors: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Product)

        if material:
            stmt = stmt.where(Product.material.ilike(f"%{material}%"))

        if category:
            cats = category.split(",")
            stmt = stmt.where(Product.category.in_(cats))

        if sizes:
            selected = sizes.split(",")
            stmt = stmt.where(or_(*[Product.sizes.contains([s]) for s in selected]))

        if colors:
            selected = colors.split(",")
            stmt = stmt.where(or_(*[Product.colors.contains([c]) for c in selected]))

        if gender:
            stmt = stmt.where(Product.gender == gender)

        if max_range:
            try:
                stmt = stmt.where(
                    Product.price >= 0,
                    Product.price <= float(max_range),
                )
            except ValueError:
                pass

        if search:
            stmt = stmt.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                    Product.brand.ilike(f"%{search}%"),
                )
            )

        result = await session.exec(stmt)
        return result.one()

    # ════════════════════════════════════════════════════════
    # FILTER METADATA
    # Returns sidebar filter options for a given gender.
    # Uses safe getattr() access for optional Product fields.
    # ════════════════════════════════════════════════════════
    async def get_filtermetadata(
        self,
        session: AsyncSession,
        gender_category: str,
    ):
        stmt = select(Product).where(Product.gender == gender_category)
        result = await session.exec(stmt)
        products = result.all()

        if not products:
            return {
                "categories": [],
                "genders": [],
                "sizes": [],
                "colors": [],
                "brands": [],
                "tags": [],
                "max_price": 2000,
            }

        # ── Categories with counts ───────────────────────────
        category_counts: dict[str, int] = {}
        for p in products:
            cat = p.category
            if cat:
                category_counts[cat] = category_counts.get(cat, 0) + 1

        categories = [
            {"name": cat, "count": count} for cat, count in category_counts.items()
        ]

        # ── Sizes ────────────────────────────────────────────
        sizes = list(
            set(size for p in products for size in (getattr(p, "sizes", None) or []))
        )

        # ── Colors ───────────────────────────────────────────
        colors = list(
            set(color for p in products for color in (getattr(p, "colors", None) or []))
        )

        # ── Brands ───────────────────────────────────────────
        brands = list(set(b for p in products if (b := getattr(p, "brand", None))))

        # ── Tags (optional field — safe access) ──────────────
        try:
            tags = list(
                set(tag for p in products for tag in (getattr(p, "tags", None) or []))
            )
        except Exception:
            tags = []

        # ── Max price ────────────────────────────────────────
        max_price = max(
            (p.price for p in products if p.price is not None),
            default=2000,
        )

        # ── All available genders (for the gender switcher) ──
        all_stmt = select(Product.gender).distinct()
        all_result = await session.exec(all_stmt)
        genders = [g for g in all_result.all() if g]

        return {
            "categories": categories,
            "genders": genders,
            "sizes": sizes,
            "colors": colors,
            "brands": brands,
            "tags": tags,
            "max_price": max_price,
        }

    # ════════════════════════════════════════════════════════
    # SINGLE PRODUCT
    # ════════════════════════════════════════════════════════
    async def get_product_by_uid(self, session: AsyncSession, p_id):
        stmt = select(Product).where(Product.id == p_id)
        result = await session.exec(stmt)
        return result.first()

    # ════════════════════════════════════════════════════════
    # CREATE
    # ════════════════════════════════════════════════════════
    async def create_product(
        self, session: AsyncSession, admin_product: ProductCreateModel
    ):
        new_product = Product(**admin_product.model_dump())
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product

    # ════════════════════════════════════════════════════════
    # DELETE
    # ════════════════════════════════════════════════════════
    async def delete_product(self, session: AsyncSession, p_id):
        product = await self.get_product_by_uid(session, p_id)
        if product is not None:
            await session.delete(product)
            await session.commit()
            return True
        return False

    # ════════════════════════════════════════════════════════
    # UPDATE
    # ════════════════════════════════════════════════════════
    async def update_product(
        self, session: AsyncSession, p_id, updated_product: ProductUpdateModel
    ):
        product = await self.get_product_by_uid(session, p_id)
        if product is not None:
            for k, v in updated_product.model_dump(exclude_unset=True).items():
                setattr(product, k, v)
            await session.commit()
            await session.refresh(product)
            return product
        return None
