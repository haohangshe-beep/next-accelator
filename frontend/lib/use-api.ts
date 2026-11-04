"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type State<T> = {
  data: T | null;
  error: string | null;
  loading: boolean;
};

export function useApi<T>(path: string | null) {
  const auth = useAuth();
  const [state, setState] = useState<State<T>>({
    data: null,
    error: null,
    loading: path !== null,
  });

  const load = useCallback(async () => {
    if (!auth.ready) {
      return;
    }
    if (path === null) {
      setState({ data: null, error: null, loading: false });
      return;
    }
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const data = await api<T>(path, { token: auth.token });
      setState({ data, error: null, loading: false });
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Something went wrong.";
      setState({ data: null, error: message, loading: false });
    }
  }, [auth.ready, auth.token, path]);

  useEffect(() => {
    void load();
  }, [load]);

  const setData = useCallback((data: T) => {
    setState({ data, error: null, loading: false });
  }, []);

  return { ...state, reload: load, setData };
}
