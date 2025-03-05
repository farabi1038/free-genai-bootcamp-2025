import { useState, useCallback, useRef, useEffect } from 'react';

interface UseApiOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: any) => void;
  immediate?: boolean;
}

type ApiFunction<T, P> = (params?: P) => Promise<T>;

function useApi<T, P = void>(
  apiFunction: ApiFunction<T, P>,
  options: UseApiOptions = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<any>(null);

  const execute = useCallback(
    async (params?: P) => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiFunction(params);
        setData(result);
        options.onSuccess?.(result);
        return result;
      } catch (err) {
        setError(err);
        options.onError?.(err);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, options]
  );

  return {
    data,
    loading,
    error,
    execute
  };
}

export default useApi; 