export function formatMoney(value, currency = "PLN") {
  if (value === undefined || value === null || value === "") return "";
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return `${value} ${currency}`;
  return new Intl.NumberFormat("pl-PL", { style: "currency", currency }).format(numeric);
}

export function formatDateTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("pl-PL", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function availabilityRange(days = 21) {
  const from = new Date();
  const to = new Date(Date.now() + days * 24 * 60 * 60 * 1000);
  return { from: from.toISOString(), to: to.toISOString() };
}

export function serviceLabel(service) {
  if (!service) return "Wybrana usługa";
  return `${service.name} · ${service.durationMinutes} min · ${formatMoney(service.basePrice, service.currency || "PLN")}`;
}

export async function loadAllTherapists(api) {
  const services = await api.services();
  const pairs = await Promise.all(
    services.map(async (service) => {
      const therapists = await api.therapistsForService(service.id);
      return therapists.map((therapist) => ({ ...therapist, serviceId: service.id, serviceName: service.name }));
    })
  );
  const byId = new Map();
  pairs.flat().forEach((therapist) => {
    const current = byId.get(therapist.id);
    if (current) {
      current.services = [...current.services, { id: therapist.serviceId, name: therapist.serviceName }];
    } else {
      byId.set(therapist.id, {
        ...therapist,
        services: [{ id: therapist.serviceId, name: therapist.serviceName }],
      });
    }
  });
  return Array.from(byId.values());
}
