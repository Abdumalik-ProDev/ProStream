from sqlmodel import SQLModel

# single place for metadata
Base = SQLModel.metadata.__self__ if hasattr(SQLModel.metadata, "__self__") else SQLModel
# simpler: export SQLModel's Base behavior - but migrations will use models import
from sqlmodel import SQLModel as _SQLModel
# We'll rely on SQLModel declarative models; keep Base as SQLModel
Base = _SQLModel