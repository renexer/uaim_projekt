import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import { AppRoutes } from './App';

function mockFetchOnce(payload, ok = true, status = ok ? 200 : 500) {
  global.fetch.mockResolvedValueOnce({
    ok,
    status,
    json: async () => payload,
  });
}

function renderAt(path = '/') {
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={[path]}>
        <AppRoutes />
      </MemoryRouter>
    </AuthProvider>
  );
}

beforeEach(() => {
  localStorage.clear();
  global.fetch = jest.fn();
});

afterEach(() => {
  jest.resetAllMocks();
});

test('renderuje stronę startową', () => {
  renderAt('/');
  expect(screen.getByRole('heading', { name: /spokojna przystań/i })).toBeInTheDocument();
  expect(screen.getAllByText(/gabinet psychologiczno-terapeutyczny/i).length).toBeGreaterThan(0);
});

test('obsługuje logowanie i zapis sesji JWT', async () => {
  mockFetchOnce({
    data: {
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      user: { id: '1', email: 'jan@example.com', firstName: 'Jan', lastName: 'Kowalski', roles: ['PATIENT'] },
    },
  });
  mockFetchOnce({ data: [] });
  mockFetchOnce({ data: [] });

  renderAt('/login');

  fireEvent.change(screen.getByLabelText(/e-mail/i), { target: { value: 'jan@example.com' } });
  fireEvent.change(screen.getByLabelText(/hasło/i), { target: { value: 'Password123!' } });
  fireEvent.click(screen.getByRole('button', { name: /zaloguj/i }));

  await waitFor(() => expect(localStorage.getItem('uaim_access_token')).toBe('access-token'));
  expect(await screen.findByRole('heading', { name: /moje wizyty/i })).toBeInTheDocument();
});

test('chroniona trasa przekierowuje niezalogowanego użytkownika do logowania', async () => {
  renderAt('/appointments');
  expect(await screen.findByRole('heading', { name: /logowanie/i })).toBeInTheDocument();
});

test('pobiera i renderuje listę usług z API', async () => {
  mockFetchOnce({
    data: [
      {
        id: 'svc-1',
        code: 'CONSULT_50',
        name: 'Konsultacja psychologiczna',
        description: 'Pierwsza konsultacja w gabinecie.',
        durationMinutes: 50,
        basePrice: '180.00',
        currency: 'PLN',
        isActive: true,
      },
    ],
  });

  renderAt('/services');

  expect(await screen.findByText('Konsultacja psychologiczna')).toBeInTheDocument();
  expect(screen.getByText(/pierwsza konsultacja/i)).toBeInTheDocument();
});

test('pokazuje komunikat błędu przy problemie API', async () => {
  mockFetchOnce({ error: { message: 'Backend niedostępny' } }, false, 503);

  renderAt('/services');

  expect(await screen.findByRole('alert')).toHaveTextContent('Backend niedostępny');
});

test('waliduje formularz rejestracji pacjenta bez zapytania do API', () => {
  renderAt('/register');
  fireEvent.click(screen.getByRole('button', { name: /zarejestruj/i }));
  expect(screen.getByRole('alert')).toHaveTextContent(/podaj imię i nazwisko/i);
  expect(global.fetch).not.toHaveBeenCalled();
});

test('renderuje terapeutów pobranych dla usług', async () => {
  mockFetchOnce({ data: [
    { id: 'svc-1', code: 'CONSULT_50', name: 'Konsultacja', description: 'Opis', durationMinutes: 50, basePrice: '180.00', currency: 'PLN' },
    { id: 'svc-2', code: 'THERAPY_50', name: 'Terapia', description: 'Opis', durationMinutes: 50, basePrice: '200.00', currency: 'PLN' },
  ] });
  mockFetchOnce({ data: [
    { id: 'th-1', fullName: 'Anna Nowak', title: 'Psycholog', bio: 'Praca ze stresem', experienceYears: 8, averageRating: '5.0', reviewsCount: 1, isActive: true },
  ] });
  mockFetchOnce({ data: [
    { id: 'th-2', fullName: 'Piotr Kowalczyk', title: 'Psychoterapeuta', bio: 'Terapia młodzieży', experienceYears: 5, averageRating: '0.0', reviewsCount: 0, isActive: true },
  ] });

  renderAt('/therapists');

  expect(await screen.findByText('Anna Nowak')).toBeInTheDocument();
  expect(screen.getByText('Piotr Kowalczyk')).toBeInTheDocument();
});

test('pokazuje dostępny termin w formularzu rezerwacji', async () => {
  mockFetchOnce({ data: [
    { id: 'svc-1', code: 'CONSULT_50', name: 'Konsultacja', description: 'Opis', durationMinutes: 50, basePrice: '180.00', currency: 'PLN' },
  ] });
  mockFetchOnce({ data: [
    { id: 'th-1', fullName: 'Anna Nowak', title: 'Psycholog', bio: 'Praca ze stresem', experienceYears: 8, averageRating: '5.0', reviewsCount: 1, isActive: true },
  ] });
  mockFetchOnce({ data: {
    service: { id: 'svc-1', name: 'Konsultacja', durationMinutes: 50 },
    range: { from: '2026-01-01T00:00:00Z', to: '2026-01-21T00:00:00Z' },
    items: [{ therapist: { id: 'th-1', fullName: 'Anna Nowak' }, slots: [{ startAt: '2026-01-03T10:00:00Z', endAt: '2026-01-03T10:50:00Z' }] }],
  } });

  renderAt('/booking?serviceId=svc-1');

  expect(await screen.findByText('Anna Nowak')).toBeInTheDocument();
  expect(screen.getByText(/3 sty 2026/i)).toBeInTheDocument();
});

test('użytkownik bez roli staff nie widzi panelu terapeuty', async () => {
  localStorage.setItem('uaim_access_token', 'token');
  localStorage.setItem('uaim_user', JSON.stringify({ id: '1', email: 'jan@example.com', firstName: 'Jan', lastName: 'Kowalski', roles: ['PATIENT'] }));
  mockFetchOnce({ data: { id: '1', email: 'jan@example.com', firstName: 'Jan', lastName: 'Kowalski', roles: ['PATIENT'] } });

  renderAt('/staff');

  expect(await screen.findByRole('heading', { name: /brak dostępu/i })).toBeInTheDocument();
});

test('renderuje historię konsultacji zalogowanego pacjenta', async () => {
  localStorage.setItem('uaim_access_token', 'token');
  localStorage.setItem('uaim_user', JSON.stringify({ id: '1', email: 'jan@example.com', firstName: 'Jan', lastName: 'Kowalski', roles: ['PATIENT'] }));
  mockFetchOnce({ data: { id: '1', email: 'jan@example.com', firstName: 'Jan', lastName: 'Kowalski', roles: ['PATIENT'] } });
  mockFetchOnce({ data: [
    {
      appointmentId: 'appt-1',
      completedAt: '2026-01-02T09:00:00Z',
      service: { name: 'Konsultacja psychologiczna' },
      therapist: { name: 'Anna Nowak', title: 'Psycholog' },
      summary: { text: 'Omówiono plan dalszej pracy.' },
      review: { exists: false },
    },
  ] });

  renderAt('/consultations');

  expect(await screen.findByText('Konsultacja psychologiczna')).toBeInTheDocument();
  expect(screen.getByText(/omówiono plan/i)).toBeInTheDocument();
});

test('renderuje panel terapeuty dla roli THERAPIST', async () => {
  localStorage.setItem('uaim_access_token', 'token');
  localStorage.setItem('uaim_user', JSON.stringify({ id: '2', email: 'anna@example.com', firstName: 'Anna', lastName: 'Nowak', roles: ['THERAPIST'] }));
  mockFetchOnce({ data: { id: '2', email: 'anna@example.com', firstName: 'Anna', lastName: 'Nowak', roles: ['THERAPIST'] } });
  mockFetchOnce({ data: [
    { id: 'appt-1', status: 'BOOKED', startAt: '2026-01-05T10:00:00Z', endAt: '2026-01-05T10:50:00Z', patientEmail: 'jan@example.com', serviceName: 'Konsultacja', therapistName: 'Anna Nowak' },
  ] });

  renderAt('/staff');

  expect(await screen.findByRole('heading', { name: /panel wizyt/i })).toBeInTheDocument();
  expect(screen.getByText(/jan@example.com/i)).toBeInTheDocument();
});

test('renderuje szczegóły terapeuty z opiniami i terminami', async () => {
  mockFetchOnce({ data: { id: 'th-1', fullName: 'Anna Nowak', title: 'Psycholog', bio: 'Praca ze stresem', experienceYears: 8, averageRating: '5.0', reviewsCount: 1, isActive: true } });
  mockFetchOnce({ data: [{ id: 'rev-1', rating: 5, comment: 'Bardzo dobra konsultacja.', createdAt: '2026-01-01T12:00:00Z' }] });
  mockFetchOnce({ data: [{ id: 'svc-1', code: 'CONSULT_50', name: 'Konsultacja', description: 'Opis', durationMinutes: 50, basePrice: '180.00', currency: 'PLN' }] });
  mockFetchOnce({ data: {
    service: { id: 'svc-1', name: 'Konsultacja', durationMinutes: 50 },
    range: { from: '2026-01-01T00:00:00Z', to: '2026-01-21T00:00:00Z' },
    items: [{ therapist: { id: 'th-1', fullName: 'Anna Nowak' }, slots: [{ startAt: '2026-01-06T11:00:00Z', endAt: '2026-01-06T11:50:00Z' }] }],
  } });

  renderAt('/therapists/th-1?serviceId=svc-1');

  expect(await screen.findByRole('heading', { name: 'Anna Nowak' })).toBeInTheDocument();
  expect(screen.getByText(/bardzo dobra konsultacja/i)).toBeInTheDocument();
  expect(screen.getByText(/6 sty 2026/i)).toBeInTheDocument();
});

test('renderuje stronę 404 dla nieznanej ścieżki', () => {
  renderAt('/nie-ma-takiej-strony');
  expect(screen.getByRole('heading', { name: /nie znaleziono strony/i })).toBeInTheDocument();
});
