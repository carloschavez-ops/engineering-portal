from models import db


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="favorites"
    )

    application = db.relationship(
        "Application",
        back_populates="favorites"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "application_id",
            name="uq_user_app"
        ),
    )