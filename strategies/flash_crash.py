"""
Flash Crash Strategy - Volatility Trading for 15-Minute Markets
Düzeltmeler:
1. SyntaxError (lines = []) giderildi.
2. _get_countdown_str() yerine current_market.get_countdown_str() kullanıldı.
3. render_status() içindeki orphan kod kaldırıldı (MarketManager zaten otomatik yapar).
4. Railway Log Sınırı (Rate Limit) koruması mevcut.
"""

import time
from dataclasses import dataclass
from typing import Dict

from lib.console import Colors
from strategies.base import BaseStrategy, StrategyConfig
from src.bot import TradingBot
from src.websocket_client import OrderbookSnapshot


@dataclass
class FlashCrashConfig(StrategyConfig):
    """Flash crash strateji yapılandırması."""
    drop_threshold: float = 0.30


class FlashCrashStrategy(BaseStrategy):
    """
    Piyasayı WebSocket üzerinden canlı izler.
    MarketManager otomatik pazar değişikliğini ve WebSocket yenilemeyi yönetir.
    """

    def __init__(self, bot: TradingBot, config: FlashCrashConfig):
        super().__init__(bot, config)
        self.flash_config = config
        self.prices.drop_threshold = config.drop_threshold
        # Railway log sınırına takılmamak için zamanlayıcı
        self.last_render_time = 0

    async def on_book_update(self, snapshot: OrderbookSnapshot) -> None:
        """Fiyat kaydı temel sınıfta yapılır."""
        pass

    async def on_tick(self, prices: Dict[str, float]) -> None:
        """Her fiyat hareketinde çöküş kontrolü yapar."""
        if not self.positions.can_open_position:
            return

        event = self.prices.detect_flash_crash()
        if event:
            self.log(
                f"FLASH CRASH: {event.side.upper()} "
                f"Düşüş {event.drop:.2f} ({event.old_price:.2f} -> {event.new_price:.2f})",
                "trade"
            )
            # Clear price history for this side so the same crash doesn't retrigger
            self.prices.clear(event.side)

            current_price = prices.get(event.side, 0)
            if current_price > 0:
                await self.execute_buy(event.side, current_price)
            else:
                self.log(f"Crash detected but no price for {event.side} (bid=0?)", "warning")

    def render_status(self, prices: Dict[str, float]) -> None:
        """Railway Log Throttling: Saniyede sadece 1 kez tablo yazdırır."""
        current_time = time.time()
        if current_time - self.last_render_time < 1.0:
            return
        self.last_render_time = current_time

        lines = []
        ws_status = f"{Colors.GREEN}WS{Colors.RESET}" if self.is_connected else f"{Colors.RED}REST{Colors.RESET}"
        countdown = self.current_market.get_countdown_str() if self.current_market else "--:--"
        stats = self.positions.get_stats()

        lines.append(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        header = (
            f"{Colors.CYAN}[{self.config.coin}]{Colors.RESET} [{ws_status}] "
            f"Ends: {countdown} | Trades: {stats['trades_closed']} "
            f"(W:{stats['winning_trades']} L:{stats['losing_trades']}) | "
            f"PnL: ${stats['total_pnl']:+.2f}"
        )
        if self.config.paper:
            header += f" | {Colors.YELLOW}[PAPER] ${self._paper_balance:.2f}{Colors.RESET}"
        lines.append(header)
        lines.append(f"{Colors.BOLD}{'='*80}{Colors.RESET}")

        up_ob = self.market.get_orderbook("up")
        down_ob = self.market.get_orderbook("down")
        lines.append(f"{Colors.GREEN}{'UP':^39}{Colors.RESET}|{Colors.RED}{'DOWN':^39}{Colors.RESET}")
        lines.append(f"{'Bid':>9} {'Size':>9} | {'Ask':>9} {'Size':>9}|{'Bid':>9} {'Size':>9} | {'Ask':>9} {'Size':>9}")
        lines.append("-" * 80)

        for i in range(5):
            u_bid = f"{up_ob.bids[i].price:>9.4f} {up_ob.bids[i].size:>9.1f}" if up_ob and i < len(up_ob.bids) else f"{'--':>9} {'--':>9}"
            u_ask = f"{up_ob.asks[i].price:>9.4f} {up_ob.asks[i].size:>9.1f}" if up_ob and i < len(up_ob.asks) else f"{'--':>9} {'--':>9}"
            d_bid = f"{down_ob.bids[i].price:>9.4f} {down_ob.bids[i].size:>9.1f}" if down_ob and i < len(down_ob.bids) else f"{'--':>9} {'--':>9}"
            d_ask = f"{down_ob.asks[i].price:>9.4f} {down_ob.asks[i].size:>9.1f}" if down_ob and i < len(down_ob.asks) else f"{'--':>9} {'--':>9}"
            lines.append(f"{u_bid} | {u_ask}|{d_bid} | {d_ask}")

        lines.append("-" * 80)
        lines.append(f"Geçmiş Veri: UP={self.prices.get_history_count('up')}/100 | Eşik: {self.flash_config.drop_threshold:.2f}")

        if self._log_buffer.messages:
            lines.append("-" * 80)
            for msg in self._log_buffer.get_messages():
                lines.append(f"  {msg}")
            self._log_buffer.clear()

        print("\033[H\033[J" + "\n".join(lines), flush=True)
