import KpiMedianPricesCard from "../KpiMedianPricesCard";
import KpiRepartitionCard from "../KpiRepartitionCard";
import KpiLogementsSociauxCard from "../KpiLogementsSociauxCard";
import KpiRevenuMensuelCard from "../KpiRevenuMensuelCard";
import KpiAccessibiliteCard from "../KpiAccessibiliteCard";

function KpiTemporalTab({
  selectedArrondissement,
  revenuProportion,
  onRevenuProportionChange,

  medianLocation,
  medianLocationLoading,
  medianLocationError,
  medianAchat,
  medianAchatLoading,
  medianAchatError,

  repartitionKpi,
  repartitionLoading,
  repartitionError,

  logementsSociauxKpi,
  logementsSociauxLoading,
  logementsSociauxError,

  accessibiliteKpi,
  accessibiliteLoading,
  accessibiliteError,
}) {
  return (
    <>
      <KpiMedianPricesCard
        selectedArrondissement={selectedArrondissement}
        medianLocation={medianLocation}
        medianLocationLoading={medianLocationLoading}
        medianLocationError={medianLocationError}
        medianAchat={medianAchat}
        medianAchatLoading={medianAchatLoading}
        medianAchatError={medianAchatError}
      />

      <KpiRepartitionCard
        selectedArrondissement={selectedArrondissement}
        repartitionKpi={repartitionKpi}
        repartitionLoading={repartitionLoading}
        repartitionError={repartitionError}
      />

      <KpiLogementsSociauxCard
        logementsSociauxKpi={logementsSociauxKpi}
        logementsSociauxLoading={logementsSociauxLoading}
        logementsSociauxError={logementsSociauxError}
      />

      <KpiRevenuMensuelCard
        selectedArrondissement={selectedArrondissement}
        accessibiliteKpi={accessibiliteKpi}
        accessibiliteLoading={accessibiliteLoading}
        accessibiliteError={accessibiliteError}
      />

      <KpiAccessibiliteCard
        selectedArrondissement={selectedArrondissement}
        revenuProportion={revenuProportion}
        onRevenuProportionChange={onRevenuProportionChange}
        accessibiliteKpi={accessibiliteKpi}
        accessibiliteLoading={accessibiliteLoading}
        accessibiliteError={accessibiliteError}
      />
    </>
  );
}

export default KpiTemporalTab;