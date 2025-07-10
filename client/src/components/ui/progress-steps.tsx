import { CheckCircle, Upload, Cog, Scissors, Download } from "lucide-react";

interface ProgressStepsProps {
  currentStep: string;
}

export function ProgressSteps({ currentStep }: ProgressStepsProps) {
  const steps = [
    {
      id: 'uploaded',
      title: 'Upload',
      description: 'Complete',
      icon: Upload,
    },
    {
      id: 'processing',
      title: 'Analysis',
      description: 'In Progress',
      icon: Cog,
    },
    {
      id: 'separating',
      title: 'Separation',
      description: 'Waiting',
      icon: Scissors,
    },
    {
      id: 'completed',
      title: 'Complete',
      description: 'Waiting',
      icon: Download,
    },
  ];

  const getStepStatus = (stepId: string) => {
    if (stepId === 'uploaded') return 'completed';
    if (stepId === 'processing' && (currentStep === 'processing' || currentStep === 'completed')) return 'active';
    if (stepId === 'separating' && currentStep === 'completed') return 'completed';
    if (stepId === 'completed' && currentStep === 'completed') return 'completed';
    return 'waiting';
  };

  const getStepStyles = (status: string) => {
    switch (status) {
      case 'completed':
        return {
          circle: 'bg-secondary text-white',
          text: 'text-gray-700',
          description: 'text-gray-500',
        };
      case 'active':
        return {
          circle: 'bg-primary text-white',
          text: 'text-gray-700',
          description: 'text-gray-500',
        };
      default:
        return {
          circle: 'bg-gray-300 text-gray-500',
          text: 'text-gray-500',
          description: 'text-gray-400',
        };
    }
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {steps.map((step) => {
        const status = getStepStatus(step.id);
        const styles = getStepStyles(status);
        const Icon = step.icon;

        return (
          <div key={step.id} className="text-center">
            <div className={`w-12 h-12 ${styles.circle} rounded-full flex items-center justify-center mx-auto mb-2 transition-colors`}>
              {status === 'completed' ? (
                <CheckCircle className="w-6 h-6" />
              ) : status === 'active' ? (
                <Icon className="w-5 h-5 animate-spin" />
              ) : (
                <Icon className="w-5 h-5" />
              )}
            </div>
            <p className={`text-sm font-medium ${styles.text}`}>{step.title}</p>
            <p className={`text-xs ${styles.description}`}>
              {status === 'completed' ? 'Complete' : 
               status === 'active' ? 'In Progress' : 'Waiting'}
            </p>
          </div>
        );
      })}
    </div>
  );
}
