"""Local file storage for generated EPUBs."""

import shutil
from datetime import datetime, timedelta
from pathlib import Path

from morning_byte.config import DeliveryConfig


class LocalDelivery:
    """Save EPUB files locally and manage retention."""

    def __init__(self, config: DeliveryConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)

    def save(self, epub_path: Path) -> Path:
        """Save/move EPUB to the output directory.

        Args:
            epub_path: Path to the generated EPUB file

        Returns:
            Path to the saved file
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate dated filename
        date_str = datetime.now().strftime("%Y-%m-%d")
        dest_name = f"morning-byte-{date_str}.epub"
        dest_path = self.output_dir / dest_name

        # Copy file (in case source is temp file)
        shutil.copy2(epub_path, dest_path)

        return dest_path

    def cleanup_old(self) -> list[Path]:
        """Remove EPUB files older than retention period.

        Returns:
            List of deleted file paths
        """
        if not self.output_dir.exists():
            return []

        cutoff = datetime.now() - timedelta(days=self.config.keep_days)
        deleted = []

        for epub_file in self.output_dir.glob("morning-byte-*.epub"):
            try:
                # Parse date from filename
                date_str = epub_file.stem.replace("morning-byte-", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff:
                    epub_file.unlink()
                    deleted.append(epub_file)
            except (ValueError, OSError):
                continue

        return deleted

    def list_digests(self) -> list[tuple[Path, datetime]]:
        """List all saved digests with their dates.

        Returns:
            List of (path, date) tuples, sorted by date descending
        """
        if not self.output_dir.exists():
            return []

        digests = []
        for epub_file in self.output_dir.glob("morning-byte-*.epub"):
            try:
                date_str = epub_file.stem.replace("morning-byte-", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                digests.append((epub_file, file_date))
            except ValueError:
                continue

        return sorted(digests, key=lambda x: x[1], reverse=True)
