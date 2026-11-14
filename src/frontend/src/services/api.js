async function parse(response) {
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed.');
  return data;
}
export const getHealth = () => fetch('/api/health').then(parse);
export const getModels = () => fetch('/api/models').then(parse);
export async function analyze(file, model) {
  const form = new FormData();
  form.append('file', file);
  form.append('model', model);
  return parse(await fetch('/api/analyze', { method: 'POST', body: form }));
}
